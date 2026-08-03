from sklearn.base import BaseEstimator, TransformerMixin

class RareManufacturerGrouper(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=100):
        self.threshold = threshold

    def fit(self, X, y=None):
        counts = X['manufacturer'].value_counts()
        self.rare_manufacturers_ = counts[counts < self.threshold].index
        return self

    def transform(self, X):
        X = X.copy()
        X['manufacturer'] = X['manufacturer'].where(
            ~X['manufacturer'].isin(self.rare_manufacturers_), 'other'
        )
        return X


class ModelTargetEncoder(BaseEstimator, TransformerMixin):
    def fit(self, X, y):
        temp = X.copy()
        temp['price'] = y
        self.model_target_map_ = temp.groupby('model')['price'].mean()
        self.overall_avg_ = y.mean()
        return self

    def transform(self, X):
        X = X.copy()
        X['model_encoded'] = X['model'].map(self.model_target_map_)
        X['model_encoded'] = X['model_encoded'].fillna(self.overall_avg_)
        X = X.drop(columns=['model'])
        return X
