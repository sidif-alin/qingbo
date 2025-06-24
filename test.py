import pandas as pd
import matplotlib.pyplot as plt
import check_sampling

train_path = "data/train.csv"
test_path = "data/test.csv"

df = check_sampling.processing_timestamp(test_path, "test")
df = check_sampling.fill_data(df)
df = check_sampling.processing_GXJ(df)
df_11 = df[(df['GXJ_A045'] != 0) & (df['GXJ_A046'] == 0)
            & (df['BMC102_A006'] != 0) & (df["BMC102_A007"] == 1)]

plt.figure(figsize=(12, 5))
plt.scatter(df_11['timestamp'], df_11['GXJ_A045'], color='black', s=10, label='GXJ_A045')
plt.xlabel("时间")
plt.ylabel("排焦量")
plt.title("GXJ_A045 排焦量在状态(皮带1开启,皮带2开启但无负载)下的变化")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 假设 df_11 是你之前筛选出的状态01的 DataFrame
df_11 = df_11.sort_values('timestamp').reset_index(drop=True)

# 计算相邻时间戳的时间差（单位秒）
df_11['time_diff'] = df_11['timestamp'].diff().dt.total_seconds()

# 将时间差不是10秒的地方作为分段点（即非连续）
df_11['segment'] = (df_11['time_diff'] != 10).cumsum()

# 按照 segment 分组，统计每组的起止时间和条数
segments = df_11.groupby('segment').agg(
    start_time=('timestamp', 'min'),
    end_time=('timestamp', 'max'),
    count=('timestamp', 'count')
).reset_index()

# 计算每段的持续时间
segments['duration_seconds'] = (segments['end_time'] - segments['start_time']).dt.total_seconds()

# 输出最长和最短连续持续时间（只考虑长度 >= 2 的）
valid_segments = segments[segments['count'] >= 2]
max_duration = valid_segments['duration_seconds'].max()
min_duration = valid_segments['duration_seconds'].min()

print(f"连续状态01 最长持续时间: {max_duration} 秒")
print(f"连续状态01 最短持续时间: {min_duration} 秒")
print("\n连续片段信息：")
print(valid_segments[['start_time', 'end_time', 'duration_seconds', 'count']])