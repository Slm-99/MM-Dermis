import pandas as pd
from datetime import datetime

# 读取原始Excel文件
input_file = r'F:\MM-Dermis\annotations\classification.xlsx'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = fr'F:\MM-Dermis\annotations\classification_processed_{timestamp}.xlsx'

# 读取数据
df = pd.read_excel(input_file)

# 创建新的数据列表
processed_rows = []

# 遍历每一行数据
for index, row in df.iterrows():
    cid = row['CID']
    sid = row['SID']
    diagnosis = row['diagnosis']
    
    # 检查SID是否包含范围
    if '-' in str(sid):
        # 拆分起始和结束编号
        parts = sid.split('-')
        start = int(parts[0])
        end = int(parts[1])
        
        # 为范围内的每个编号创建一行
        for i in range(start, end + 1):
            new_sid = f"{i:02d}"  # 格式化为两位数字
            processed_rows.append({
                'CID': cid,
                'SID': new_sid,
                'diagnosis': diagnosis
            })
    else:
        # 单个SID值,直接添加
        processed_rows.append({
            'CID': cid,
            'SID': str(sid),  # 确保SID保持为字符串格式
            'diagnosis': diagnosis
        })

# 创建新的DataFrame
processed_df = pd.DataFrame(processed_rows)

# 保存到新的Excel文件,使用openpyxl引擎
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    processed_df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    # 获取工作表并设置CID和SID列格式为文本
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # 设置CID列(A列)和SID列(B列)为文本格式
    for row in range(2, len(processed_df) + 2):  # 从第2行开始(跳过标题)
        # CID列(A列) - 设置为4位数字格式
        cell_cid = worksheet.cell(row=row, column=1)
        cell_cid.value = str(cell_cid.value).zfill(4)  # 确保是四位数字格式
        cell_cid.number_format = '@'  # '@'表示文本格式
        
        # SID列(B列) - 设置为2位数字格式
        cell_sid = worksheet.cell(row=row, column=2)
        cell_sid.value = str(cell_sid.value).zfill(2)  # 确保是两位数字格式
        cell_sid.number_format = '@'  # '@'表示文本格式

print(f"处理完成!")
print(f"原始数据行数: {len(df)}")
print(f"处理后数据行数: {len(processed_df)}")
print(f"输出文件: {output_file}")

