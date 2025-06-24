import pandas as pd
import check_sampling
from scipy.stats import skew, kurtosis


def add_statistical_features(df: pd.DataFrame):
    df = df.sort_values("timestamp").set_index("timestamp")

    feature_windows = {
        "30min": "30min",
        "1h": "1h",
        "2h": "2h",
        "3h": "3h"
    }

    for name, window in feature_windows.items():
        for col in ['GXJ_A045', 'GXJ_A046']:
            col_base = col.split('_')[-1]

            # 滚动窗口对象
            roll = df[col].rolling(window)

            df[f'{col_base}_mean_{name}'] = roll.mean()
            df[f'{col_base}_std_{name}'] = roll.std()
            df[f'{col_base}_min_{name}'] = roll.min()
            df[f'{col_base}_max_{name}'] = roll.max()
            df[f'{col_base}_sum_{name}'] = roll.sum()
            df[f'{col_base}_median_{name}'] = roll.median()
            df[f'{col_base}_skew_{name}'] = roll.apply(skew, raw=True)
            df[f'{col_base}_kurt_{name}'] = roll.apply(kurtosis, raw=True)

    df.fillna(method='bfill', inplace=True)
    df = df.reset_index()
    return df


def processing(path, mode):
    df = check_sampling.processing_timestamp(path, mode)
    df = check_sampling.processing_GXJ(df)
    df = check_sampling.fill_data(df)
    df = add_statistical_features(df)
    return df

if __name__ == "__main__":
    train_path = "data/train.csv"
    test_path = "data/test.csv"
    df = processing(train_path, "train")
    df2 = processing(test_path, "test")
    df.to_csv("data/pro_train.csv", index=False)
    df2.to_csv("data/pro_test.csv", index=False)