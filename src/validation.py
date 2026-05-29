import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error

def create_local_validation_set(df_surface: pd.DataFrame, mask_fraction: float = 0.10, random_seed: int = 42):
    """
    Takes the volatility surface, identifies strictly known (observed) values,
    and artificially masks a percentage of them to create a local testing ground.
    """
    np.random.seed(random_seed)
    
    # We can only test on rows where we actually know the true IV
    known_mask = df_surface['implied_volatility'].notna()
    known_indices = df_surface[known_mask].index
    
    # Randomly select indices to hide
    num_to_hide = int(len(known_indices) * mask_fraction)
    hidden_indices = np.random.choice(known_indices, size=num_to_hide, replace=False)
    
    # Create the test dataframe
    df_test = df_surface.copy()
    
    # Store the ground truth before masking
    ground_truth = df_test.loc[hidden_indices, 'implied_volatility'].copy()
    
    # Artificially mask the data
    df_test.loc[hidden_indices, 'implied_volatility'] = np.nan
    
    return df_test, hidden_indices, ground_truth

def calculate_score(predictions: pd.Series, ground_truth: pd.Series):
    """
    Calculates the exact Kaggle judging metric (MSE).
    """
    mse = mean_squared_error(ground_truth, predictions)
    return mse