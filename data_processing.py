import pandas as pd
import os

# 1. 设置文件名
input_file = '12.22_1_100_finish_score.xlsx'  # 读取最原始的文件
output_file = '12.22_1_100_finish_score_final.xlsx' # 保存为最终文件

if not os.path.exists(input_file):
    print(f"错误：找不到文件 {input_file}")
else:
    print("正在读取 Excel 文件...")
    df = pd.read_excel(input_file)

    # -------------------------------------------------
    # 第一步：把第一列（Input）的空值向下填充
    # -------------------------------------------------
    print("正在填充第一列数据...")
    df.iloc[:, 0] = df.iloc[:, 0].ffill()

    # -------------------------------------------------
    # 第二步：删除“打分”列为空的行
    # -------------------------------------------------
    print("正在删除没有打分的行...")
    # subset=['打分'] 指定了只检查“打分”这一列
    # 如果这一列是空值 (NaN)，整行就会被删除
    df = df.dropna(subset=['打分'])

    # 4. 保存结果
    print("正在保存最终文件...")
    df.to_excel(output_file, index=False)

    print(f"处理成功！\n最终文件已保存为: {output_file}")