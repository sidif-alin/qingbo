import pandas as pd


def processing_timestamp(file_path, mode="train"):
    parse_formats = {
        "train":"%Y/%m/%d %H:%M",
        "test":"%Y-%m-%d %H:%M:%S"
    }
    df = pd.read_csv(file_path, header=0, index_col=0 if mode=="test" else None)
    df.columns = ['timestamp', 'GXJ_A045', 'GXJ_A046', 'BMC102_A006', 'BMC102_A007', 'GXJ_ZDGLQ_GD']

    if mode == "train":
        df["timestamp"] = pd.to_datetime(df["timestamp"], format=parse_formats.get("train"))
        # 统一化时间戳，训练集和测试集时间戳方式不一致，统一到s级
        df["group_index"] = df.groupby("timestamp").cumcount()
        df["timestamp"] += pd.to_timedelta(df["group_index"] * 10, unit='s')
        df.drop(columns='group_index', inplace=True)

    elif mode == "test":
        df["timestamp"] = pd.to_datetime(df["timestamp"], format=parse_formats.get("tests"))
        # 将测试集的时间戳标准化，通过观察发现每10s记录一次，但是存在几秒的误差，统一缩进到10
        def round_to(timestamp:pd.Timestamp):
            seconds = timestamp.second
            _round = int(round(seconds / 10.0) * 10) % 60
            return timestamp.replace(second=_round)
        df['timestamp'] = df['timestamp'].apply(round_to)

    else:
        raise Exception("mode error")
    df = df[~((df["BMC102_A006"] == 1) & (df["BMC102_A007"] == 1))]
    return df


def inspect_timestamp(df:pd.DataFrame):
    """
    检查训练集和测试集每分钟采样数时候有缺失值，每分钟6次采样率
    :param df:
    :return:
    """
    df['minute'] = df['timestamp'].dt.floor('min')
    group_counts = df.groupby('minute').size()
    miss_groups = group_counts[group_counts != 6]
    if not miss_groups.empty:
        print("异常样本数量：",len(miss_groups))
        for minute in miss_groups.index:
            print(df[df['minute'] == minute])

# df = processing_timestamp("./data/train.csv", "train")
# inspect_timestamp(df)
# df = processing_timestamp("./data/test.csv", "test")
# inspect_timestamp(df)

def processing_GXJ(df:pd.DataFrame):
    df.loc[df['GXJ_A045'] > 200, 'GXJ_A045'] = 0
    df.loc[df['GXJ_A045'] < 110, 'GXJ_A045'] = 0
    df.loc[df['GXJ_A046'] > 200, 'GXJ_A046'] = 0
    df.loc[df['GXJ_A046'] < 110, 'GXJ_A046'] = 0
    return df

def fill_data(df:pd.DataFrame):
    df = df.drop_duplicates(subset='timestamp', keep='first')
    full_time_timestamp = pd.date_range(start=df['timestamp'].min(),
                                        end=df['timestamp'].max(),
                                        freq='10s')
    df = df.set_index('timestamp').reindex(full_time_timestamp)

    df = df.ffill()

    df = df.rename_axis('timestamp').reset_index()

    return df