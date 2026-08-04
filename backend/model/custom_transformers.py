from sklearn.base import BaseEstimator, TransformerMixin


class RareManufacturerGrouper(BaseEstimator, TransformerMixin):
    """Groups manufacturers with few listings into a single 'other' category."""

    def __init__(self, threshold=100):
        # Manufacturers with fewer listings than this threshold get grouped as 'other'
        self.threshold = threshold

    def fit(self, X, y=None):
        # Learn which manufacturers are rare from the training data only (prevents data leakage)
        counts = X['manufacturer'].value_counts()
        self.rare_manufacturers_ = counts[counts < self.threshold].index
        return self

    def transform(self, X):
        X = X.copy()
        # Replace rare manufacturers with the string 'other'
        X['manufacturer'] = X['manufacturer'].where(
            ~X['manufacturer'].isin(self.rare_manufacturers_), 'other'
        )
        return X


class ModelTargetEncoder(BaseEstimator, TransformerMixin):
    """Replaces each car `model` with that model's average training price."""

    def fit(self, X, y):
        temp = X.copy()
        temp['price'] = y
        # Calculate the average price for each unique car model using training data
        self.model_target_map_ = temp.groupby('model')['price'].mean()
        # Save overall average price as a fallback for unseen models during inference
        self.overall_avg_ = y.mean()
        return self

    def transform(self, X):
        X = X.copy()
        # Map the car model names to their learned average prices
        X['model_encoded'] = X['model'].map(self.model_target_map_)
        # Fill missing/unknown models with the overall dataset average
        X['model_encoded'] = X['model_encoded'].fillna(self.overall_avg_)
        # Drop the raw text column since it has been successfully encoded into a number
        X = X.drop(columns=['model'])
        return X