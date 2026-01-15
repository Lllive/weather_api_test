import pandas as pd
import ast
import re

def clean_gloss_text(text):
    """
    清洗函数：将 JSON/字典格式的字符串转换为纯文本句子，并去除空格
    """
    if pd.isna(text) or text == "":
        return ""
    
    # 1. 尝试解析为 Python 对象 (处理列表/字典结构)
    try:
        # 如果是字符串形式的字典/列表，尝试转换
        data = ast.literal_eval(text)
        
        # 情况 A: 如果是字典，且有 "gloss" 键
        if isinstance(data, dict) and "gloss" in data:
            words = data["gloss"]
            # 【修改点1】：这里改成 "".join(words)，即直接拼接，不加空格
            return "".join(words) 
            
        # 情况 B: 如果直接是列表
        elif isinstance(data, list):
            # 【修改点2】：同上，列表直接拼接
            return "".join(data)
            
    except (ValueError, SyntaxError):
        # 如果解析失败，进入暴力清洗模式
        pass

    # 2. 暴力清洗模式 (如果上面解析失败)
    # 删除 { } [ ] " ' : gloss 等符号
    cleaned = re.sub(r'[{"\'}[]:,]', '', text)
    cleaned = cleaned.replace('gloss', '')
    
    # 【修改点3】：去除所有的空白字符（包括空格、换行、制表符）
    cleaned = re.sub(r'\s+', '', cleaned)
    
    return cleaned

def main():
    # --- 配置区域 ---
    # 输入文件名 (保持你截图中的原始文件名)
    input_file = "weather_result_20260105_145344.xlsx" 
    # 输出文件名
    output_file = "weather_result_cleaned.xlsx"
    # ----------------
    
    print(f"正在读取文件: {input_file} ...")
    
    try:
        # 读取 Excel
        df = pd.read_excel(input_file)
        
        # 检查是否存在 'hksl_output' 列
        if 'hksl_output' not in df.columns:
            print("错误：未在文件中找到 'hksl_output' (B列)。请检查列名。")
            return

        print("正在处理数据，清洗 B 列格式并移除空格...")
        
        # 创建一个新列 'hksl_cleaned' 存放清洗后的句子
        df['hksl_cleaned'] = df['hksl_output'].apply(clean_gloss_text)
        
        # (可选) 打印前几行看看效果
        print("\n--- 预览前 5 行清洗结果 (已去空格) ---")
        print(df[['hksl_output', 'hksl_cleaned']].head().to_string())
        print("------------------------------------\n")

        # 保存结果
        df.to_excel(output_file, index=False)
        print(f"✅ 处理完成！结果已保存为: {output_file}")
        
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {input_file}，请确认文件在当前目录下。")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    main()