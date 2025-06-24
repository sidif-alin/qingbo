import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import check_sampling
from matplotlib import rcParams


train_path = "data/train.csv"
test_path = "data/test.csv"
rcParams['font.sans-serif'] = ['Arial Unicode MS']
rcParams['axes.unicode_minus'] = False
def processing(path, mode):
    df = check_sampling.processing_timestamp(path, mode)
    df = check_sampling.fill_data(df)
    df = check_sampling.processing_GXJ(df)

    return df


def plot_selected_conditions(df: pd.DataFrame):
    # df['date'] = df['timestamp'].dt.date
    # first_day = df['date'].min()
    # df = df[df['date'] == first_day]
    fig, axs = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle("皮带排焦量随时间变化（分状态）", fontsize=16)

    # 状态01：仅皮带2运行
    cond_01 = df[(df['BMC102_A006'] == 0) & (df['BMC102_A007'] == 1)]
    axs[0].plot(cond_01['timestamp'], cond_01['GXJ_A046'], color='green', label="皮带2排焦量")

    # 标注异常点：皮带2运行时皮带1数据却不为0
    anomaly_01 = cond_01[(cond_01['GXJ_A045'] != 0) & (cond_01['GXJ_A046'] == 0)]
    axs[0].scatter(anomaly_01['timestamp'], anomaly_01['GXJ_A045'], color='red', marker='x', label="异常：皮带1≠0")

    axs[0].set_title("状态01：仅皮带2运行")
    axs[0].legend()

    # 状态10：仅皮带1运行
    cond_10 = df[(df['BMC102_A006'] == 1) & (df['BMC102_A007'] == 0)]
    axs[1].plot(cond_10['timestamp'], cond_10['GXJ_A045'], color='blue', label="皮带1排焦量")

    # 标注异常点：皮带1运行时皮带2数据却不为0
    anomaly_10 = cond_10[(cond_10['GXJ_A045'] == 0) & (cond_10['GXJ_A046'] != 0)]
    axs[1].scatter(anomaly_10['timestamp'], anomaly_10['GXJ_A046'], color='red', marker='x', label="异常：皮带2≠0")

    axs[1].set_title("状态10：仅皮带1运行")
    axs[1].legend()

    cond_11 = df[
        (df['BMC102_A006'] == 1) &
        (df['BMC102_A007'] == 1) &
        (df['GXJ_A045'] != 0) &
        (df['GXJ_A046'] != 0)
    ]
    axs[2].plot(cond_11['timestamp'], cond_11['GXJ_A045'], color='blue', label="皮带1排焦量")
    axs[2].plot(cond_11['timestamp'], cond_11['GXJ_A046'], color='green', label="皮带2排焦量")
    axs[2].set_title("状态11：两条皮带同时运行（排焦量均非零）")
    axs[2].legend()

    for ax in axs:
        ax.set_xlabel("时间")
        ax.set_ylabel("排焦量")

    plt.tight_layout()
    plt.show()


def plot_GCJ_with_GD(df:pd.DataFrame):
    df['排焦总量'] = df['GXJ_A045'] + df['GXJ_A046']

    plt.figure(figsize=(16, 5))

    # 皮带1
    plt.subplot(1, 3, 1)
    plt.scatter(df['GXJ_A045'], df['GXJ_ZDGLQ_GD'], alpha=0.3, label="皮带1")
    plt.xlabel("GXJ_A045（皮带1排焦量）")
    plt.ylabel("振幅 GXJ_ZDGLQ_GD")
    plt.title("皮带1排焦量 vs 振幅")
    plt.grid(True)

    # 皮带2
    plt.subplot(1, 3, 2)
    plt.scatter(df['GXJ_A046'], df['GXJ_ZDGLQ_GD'], alpha=0.3, color="orange", label="皮带2")
    plt.xlabel("GXJ_A046（皮带2排焦量）")
    plt.ylabel("振幅 GXJ_ZDGLQ_GD")
    plt.title("皮带2排焦量 vs 振幅")
    plt.grid(True)

    # 排焦总量
    plt.subplot(1, 3, 3)
    plt.scatter(df['排焦总量'], df['GXJ_ZDGLQ_GD'], alpha=0.3, color="green", label="总排焦量")
    plt.xlabel("GXJ_A045 + GXJ_A046（排焦总量）")
    plt.ylabel("振幅 GXJ_ZDGLQ_GD")
    plt.title("总排焦量 vs 振幅")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # df = processing(train_path, "train")
    df = processing(test_path, "test")
    # plot_selected_conditions(df)
    # plot_GCJ_with_GD()