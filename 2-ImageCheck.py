import pandas as pd
import os
from datetime import datetime

# 读取索引文件
index_file = r'F:\MM-Dermis\annotations\classification_processed_20260311_232831.xlsx'
images_base_dir = r'F:\MM-Dermis\images'

print("正在读取索引文件...")
df = pd.read_excel(index_file, dtype={'CID': str, 'SID': str})
print(f"共需检查 {len(df)} 条记录\n")

# 存储检查结果
results = []
complete_count = 0
incomplete_count = 0
missing_dir_count = 0

# 遍历每条记录
for index, row in df.iterrows():
    cid = row['CID']
    sid = row['SID']
    
    # 构建目录路径
    image_dir = os.path.join(images_base_dir, f"CID-{cid}", sid)
    
    # 构建预期的文件名
    expected_files = [
        f"CID_{cid}_{sid}.jpg",
        f"CID_{cid}_{sid}_Amber.jpg",
        f"CID_{cid}_{sid}_Pola.jpg",
        f"CID_{cid}_{sid}_Wood.jpg"
    ]
    
    # 检查目录是否存在
    if not os.path.exists(image_dir):
        results.append({
            'CID': cid,
            'SID': sid,
            'Status': '目录不存在',
            'Missing_Files': 'All',
            'Directory': image_dir
        })
        missing_dir_count += 1
        continue
    
    # 检查每个文件是否存在
    missing_files = []
    for file_name in expected_files:
        file_path = os.path.join(image_dir, file_name)
        if not os.path.exists(file_path):
            missing_files.append(file_name)
    
    # 记录结果
    if len(missing_files) == 0:
        results.append({
            'CID': cid,
            'SID': sid,
            'Status': '完整',
            'Missing_Files': '',
            'Directory': image_dir
        })
        complete_count += 1
    else:
        results.append({
            'CID': cid,
            'SID': sid,
            'Status': '不完整',
            'Missing_Files': ', '.join(missing_files),
            'Directory': image_dir
        })
        incomplete_count += 1

# 创建结果DataFrame
results_df = pd.DataFrame(results)

# 生成报告，保存在当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
report_file = os.path.join(current_dir, 'image_check_report.txt')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("图片数据集完整性检查报告\n")
    f.write("=" * 80 + "\n")
    f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"索引文件: {index_file}\n")
    f.write(f"图片目录: {images_base_dir}\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("统计摘要:\n")
    f.write("-" * 80 + "\n")
    f.write(f"总记录数: {len(df)}\n")
    f.write(f"完整记录: {complete_count} ({complete_count/len(df)*100:.2f}%)\n")
    f.write(f"不完整记录: {incomplete_count} ({incomplete_count/len(df)*100:.2f}%)\n")
    f.write(f"目录不存在: {missing_dir_count} ({missing_dir_count/len(df)*100:.2f}%)\n")
    f.write("=" * 80 + "\n\n")
    
    # 如果有问题,列出详细信息
    if incomplete_count > 0 or missing_dir_count > 0:
        f.write("问题记录详情:\n")
        f.write("-" * 80 + "\n")
        problem_records = results_df[results_df['Status'] != '完整']
        for idx, record in problem_records.iterrows():
            f.write(f"\nCID: {record['CID']}, SID: {record['SID']}\n")
            f.write(f"状态: {record['Status']}\n")
            f.write(f"目录: {record['Directory']}\n")
            if record['Missing_Files']:
                f.write(f"缺失文件: {record['Missing_Files']}\n")

# 保存缺失清单到CSV
if incomplete_count > 0 or missing_dir_count > 0:
    missing_file = r'd:\VscFiles\Dermatoses\missing_images.csv'
    problem_records = results_df[results_df['Status'] != '完整']
    problem_records.to_csv(missing_file, index=False, encoding='utf-8-sig')
    print(f"缺失清单已保存到: {missing_file}")

# 控制台输出统计摘要
print("=" * 80)
print("检查完成!")
print("=" * 80)
print(f"总记录数: {len(df)}")
print(f"完整记录: {complete_count} ({complete_count/len(df)*100:.2f}%)")
print(f"不完整记录: {incomplete_count} ({incomplete_count/len(df)*100:.2f}%)")
print(f"目录不存在: {missing_dir_count} ({missing_dir_count/len(df)*100:.2f}%)")
print("=" * 80)
print(f"\n详细报告已保存到: {report_file}")

if incomplete_count == 0 and missing_dir_count == 0:
    print("\n[OK] 所有图片数据完整!")
else:
    print(f"\n[WARNING] 发现 {incomplete_count + missing_dir_count} 条记录存在问题")
    print("请查看详细报告和缺失清单")

