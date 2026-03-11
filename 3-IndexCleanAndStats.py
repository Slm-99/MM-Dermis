import os
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import font_manager
# 设置字体为系统里的中文字体（Windows 常用 SimHei 或 Microsoft YaHei）
plt.rcParams['font.sans-serif'] = ['SimHei']      # 或 ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False        # 解决负号显示为方块的问题

import pandas as pd


# 当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# === 路径配置（根据需要修改） ===
# 索引文件：由 1-DataProcess.py 生成的 classification_processed_*.xlsx
index_file = r'F:\MM-Dermis\annotations\classification_processed_20260311_232831.xlsx'

# 图片根目录（与 2-ImageCheck.py 中保持一致）
images_base_dir = r'F:\MM-Dermis\images'


def has_all_modalities(row) -> bool:
    """检查该样本是否 4 个模态图片都存在。"""
    cid = row['CID']
    sid = row['SID']

    image_dir = os.path.join(images_base_dir, f"CID-{cid}", sid)
    if not os.path.exists(image_dir):
        return False

    expected_files = [
        f"CID_{cid}_{sid}.jpg",
        f"CID_{cid}_{sid}_Amber.jpg",
        f"CID_{cid}_{sid}_Pola.jpg",
        f"CID_{cid}_{sid}_Wood.jpg",
    ]

    for file_name in expected_files:
        file_path = os.path.join(image_dir, file_name)
        if not os.path.exists(file_path):
            return False

    return True


def main():
    print("正在读取索引文件...")
    df = pd.read_excel(index_file, dtype={'CID': str, 'SID': str})
    print(f"原始索引条目数: {len(df)}")

    # 过滤掉任意模态缺失的样本
    print("正在检查每条记录是否 4 个模态全部存在...")
    mask = df.apply(has_all_modalities, axis=1)
    clean_df = df[mask].reset_index(drop=True)

    removed_count = len(df) - len(clean_df)
    print(f"清洗后索引条目数: {len(clean_df)}")
    print(f"因缺失模态被剔除的条目数: {removed_count}")

    # 保存清洗后的索引到当前目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    clean_index_path = os.path.join(current_dir, f'classification_clean_{timestamp}.xlsx')
    clean_df.to_excel(clean_index_path, index=False)
    print(f"清洗后的索引已保存到: {clean_index_path}")

    # 统计每一类（diagnosis）的分布
    if 'diagnosis' not in clean_df.columns:
        print("警告: 清洗后的索引中没有 'diagnosis' 列，无法统计类别分布。")
        return

    class_counts = clean_df['diagnosis'].value_counts().sort_index()
    print("\n各类别样本数量分布:")
    for cls, cnt in class_counts.items():
        print(f"{cls}: {cnt}")

    # 绘制长条图并保存到 results 文件夹（横向条形图）
    results_dir = os.path.join(current_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # 横向条形图：y 轴为类别，x 轴为数量
    plt.figure(figsize=(16, max(4, len(class_counts) * 0.5)))
    class_counts.sort_values(ascending=True).plot(kind='barh')
    plt.ylabel('诊断类别')
    plt.xlabel('样本数量')
    plt.title('清洗后各类别样本分布')
    plt.tight_layout()

    plot_path = os.path.join(results_dir, f'class_distribution_{timestamp}.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()

    print(f"\n类别分布长条图已保存到: {plot_path}")


if __name__ == '__main__':
    main()

