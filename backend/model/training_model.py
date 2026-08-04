import pandas as pd
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import joblib

from custom_transformers import RareManufacturerGrouper, ModelTargetEncoder


# ---------------------------------------------------------------------------
# Get the data
# ---------------------------------------------------------------------------
# Cleaning and downsampling already happened in Colab
# This file is the already-clean, already-downsampled
# 100k-row output of that process.

# Ensure we are looking in the exact directory this script is running from
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'cleaned_craigslist_100k.csv')

df = pd.read_csv(csv_path)
print("Loaded shape:", df.shape)
df.info()


# ---------------------------------------------------------------------------
# Split BEFORE any preprocessing that "learns" from data
# ---------------------------------------------------------------------------
# Splitting first, then building every preprocessing step (imputer, encoders,
# target encoder, scaler) as pipeline steps that get FIT only on X_train, is
# what prevents data leakage. Nothing below this line "looks at" X_test/y_test
# until the very final evaluation step.

X = df.drop(columns=['price'])
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# ---------------------------------------------------------------------------
# Build the preprocessing pipeline
# ---------------------------------------------------------------------------

# Columns imputed with a new "Unknown" category: missingness rate is high
# enough (20-70%+) that we shouldn't assume it's random, and "Unknown" lets
# the model learn from missingness itself if it turns out to matter.
unknown_cols = ['condition', 'cylinders', 'drive', 'size', 'type']

# Columns imputed with their most frequent value: missingness rate is small
# enough (<2%) that treating it as random noise is a reasonable simplification.
mode_cols = ['fuel', 'title_status', 'transmission']

# Columns with no natural order -> one-hot encoded (each category becomes
# its own 0/1 column, so no false ranking is invented between categories).
nominal_cols = ['manufacturer', 'fuel', 'title_status', 'transmission', 'drive', 'type']

# Plain numeric columns -> standardized (mean 0, std 1). XGBoost doesn't
# strictly need this (tree splits are scale-independent), but it's included
# as good practice for any future model swap that DOES need it.
numeric_cols = ['year', 'odometer']

# Ordinal orderings -- verified against the dataset's actual unique values,
# worst/smallest to best/largest. 'Unknown' is placed at the low end as a
# practical compromise, not a claim that unknown = worst.
condition_order = [['Unknown', 'salvage', 'fair', 'good', 'excellent', 'like new', 'new']]
size_order = [['Unknown', 'sub-compact', 'compact', 'mid-size', 'full-size']]
cylinder_order = [['Unknown', 'other', '3 cylinders', '4 cylinders', '5 cylinders',
                    '6 cylinders', '8 cylinders', '10 cylinders', '12 cylinders']]

# `verbose_feature_names_out=False` + `.set_output(transform="pandas")` keeps
# column names clean and unprefixed as data flows through each step -- this
# is required for our custom transformers, which look up columns by name
# (e.g. X['manufacturer']), not by position.
imputer_transformer = ColumnTransformer(
    transformers=[
        ('unknown_fill', SimpleImputer(strategy='constant', fill_value='Unknown'), unknown_cols),
        ('mode_fill', SimpleImputer(strategy='most_frequent'), mode_cols),
    ],
    remainder='passthrough',
    verbose_feature_names_out=False,
).set_output(transform="pandas")

encoding_transformer = ColumnTransformer(
    transformers=[
        ('condition_ord', OrdinalEncoder(categories=condition_order), ['condition']),
        ('size_ord', OrdinalEncoder(categories=size_order), ['size']),
        ('cylinder_ord', OrdinalEncoder(categories=cylinder_order), ['cylinders']),
        ('nominal_ohe', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), nominal_cols),
        ('scale', StandardScaler(), numeric_cols),
    ],
    remainder='passthrough',
    verbose_feature_names_out=False,
).set_output(transform="pandas")


# ---------------------------------------------------------------------------
# Assemble the PREPROCESSING pipeline
# ---------------------------------------------------------------------------

preprocessing_pipeline = Pipeline([
    ('imputer', imputer_transformer),
    ('manufacturer_grouper', RareManufacturerGrouper(threshold=100)),
    ('model_encoder', ModelTargetEncoder()),
    ('encoding', encoding_transformer),
])


# ---------------------------------------------------------------------------
# Fit preprocessing, transform data, train + tune the model
# ---------------------------------------------------------------------------
# Fit preprocessing on training data only, then transform both train and
# test using what was learned (same fit-on-train, apply-to-both discipline
# as every individual step already followed).

preprocessing_pipeline.fit(X_train, y_train)
X_train_processed = preprocessing_pipeline.transform(X_train)
X_test_processed = preprocessing_pipeline.transform(X_test)

param_grid = {
    'n_estimators': [100, 300, 500],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 5, 7],
}

grid_search = GridSearchCV(
    estimator=XGBRegressor(random_state=42, n_jobs=-1),
    param_grid=param_grid,
    cv=5,
    scoring='neg_mean_absolute_error',
    verbose=2,
    n_jobs=-1,
)

print("Starting hyperparameter search (this can take a while)...")
grid_search.fit(X_train_processed, y_train)
print("Best parameters:", grid_search.best_params_)

best_model = grid_search.best_estimator_


# ---------------------------------------------------------------------------
# Evaluate on the held-out test set (first and only time it's used)
# ---------------------------------------------------------------------------

predictions = best_model.predict(X_test_processed)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"\nFinal Test MAE: ${mae:,.2f}")
print(f"Final Test R^2: {r2:.4f}")

importances = pd.Series(best_model.feature_importances_, index=X_train_processed.columns)
print("\nTop 10 most important features:")
print(importances.sort_values(ascending=False).head(10))


# ---------------------------------------------------------------------------
# Bundle and Save the FINAL Pipeline
# ---------------------------------------------------------------------------
# We bundle the preprocessing and the winning model together. This allows 
# app.py to load ONE file and just call .predict() on it directly!

final_pipeline = Pipeline([
    ('preprocessing', preprocessing_pipeline),
    ('xgb_model', best_model)
])

# Use the bulletproof OS method to save it right next to this script
save_path = os.path.join(current_dir, 'car_price_pipeline.joblib')

joblib.dump(final_pipeline, save_path)
print(f"\nSuccessfully saved the complete pipeline to: {save_path}")