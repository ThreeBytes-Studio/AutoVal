from sklearn.base import BaseEstimator, TransformerMixin


class RareManufacturerGrouper(BaseEstimator, TransformerMixin):
    """
    Groups low-frequency manufacturers into a single 'other' category.

    Manufacturers with fewer than `threshold` listings in the training data
    like Ferrari Land Rover don't have enough examples for the model to
    learn anything reliable about them individually, so they're collapsed
    into one shared category instead of each getting their own encoded column.
    """

    def __init__(self, threshold=100):
        self.threshold = threshold

    def fit(self, X, y=None):
        # Learn which manufacturers are rare, using training data only
        counts = X['manufacturer'].value_counts()
        self.rare_manufacturers_ = counts[counts < self.threshold].index
        return self

    def transform(self, X):
        # Replace any rare manufacturer with 'other'; leave common ones as-is
        X = X.copy()
        X['manufacturer'] = X['manufacturer'].where(
            ~X['manufacturer'].isin(self.rare_manufacturers_), 'other'
        )
        return X


class ModelTargetEncoder(BaseEstimator, TransformerMixin):
    """
    Replaces each car model like civic and f-150 with the average price
    of that model, learned from training data only.

    `model` has thousands of unique values, too many for one-hot encoding,
    but it's one of the strongest predictors of price — target encoding
    turns it into a single informative number instead of dropping it.

    Any model unseen during training (fit) falls back to the overall average
    training price, rather than being left blank.
    """
    
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