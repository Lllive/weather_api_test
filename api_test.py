import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# 加载当前目录下的 .env 文件
load_dotenv()

# ================= 配置区域 =================
# 1. 文件设置
INPUT_FILE = 'weather_data_150.csv'
PROMPT_FILE = 'prompt_template.txt'

# 2. API 设置
API_URL = os.getenv("OPENAI_API_URL")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME") # 或者 "gpt-4", 根据你的需求修改

# 3. 模拟模式开关
# True = 不真的发请求，只模拟返回结果（用于测试代码流程）
# False = 真实发送请求给 API (消耗 Token)
MOCK_MODE = False 

# ================= 辅助函数：读取 Prompt =================
def load_prompt():
    """
    从 txt 文件中读取 system prompt。
    如果文件不存在，返回 None。
    """
    if not os.path.exists(PROMPT_FILE):
        print(f"❌ 错误: 找不到文件 {PROMPT_FILE}")
        return None
    
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print(f"⚠️ 警告: {PROMPT_FILE} 文件是空的")
                return None
            return content
    except Exception as e:
        print(f"❌ 读取文件出错: {e}")
        return None

# ================= API 调用函数 =================
def call_translation_api(text, system_prompt):
    """
    调用 API 将文本发送给大模型
    参数:
      text: CSV 中的输入文本 (User Content)
      system_prompt: 从 txt 读取的提示词 (System Content)
    """
    if MOCK_MODE:
        # 模拟返回
        return {
            "hksl": f"[模拟结果] {text[:10]}... -> HKSL翻译",
            "status": "mock_success"
        }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 组装标准的 OpenAI Chat 格式 Payload
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": text
            }
        ],
        "temperature": 0.1 # 温度越低，结果越稳定
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            try:
                # 1. 检查是否存在 'gloss' 键
                if "gloss" in data:
                    gloss_list = data["gloss"]
                    
                    # 2. 检查是否为列表
                    if isinstance(gloss_list, list):
                        # 3. 将列表拼接成字符串，用空格隔开
                        # 例如: ["明天", "天气", "好"] -> "明天 天气 好"
                        result_text = " ".join([str(item) for item in gloss_list])
                        return {"hksl": result_text, "status": "success"}
                    else:
                        # 如果 gloss 存在但不是列表（比如直接是字符串）
                        return {"hksl": str(gloss_list), "status": "success"}
                
                # 兼容旧代码：如果 API 偶尔返回标准格式
                elif "choices" in data:
                    return {"hksl": data['choices'][0]['message']['content'], "status": "success"}
                
                else:
                    return {"hksl": f"未知JSON结构: {data}", "status": "parse_error"}

            except Exception as parse_e:
                return {"hksl": f"解析异常: {parse_e}", "status": "parse_error"}
        else:
            return {"hksl": f"API Error: {response.status_code} - {response.text}", "status": "fail"}
            
    except Exception as e:
        return {"hksl": f"Exception: {str(e)}", "status": "error"}

# ================= 主程序逻辑 =================
def main():
    # --- 1. 预检查：加载 Prompt ---
    print("正在加载 System Prompt...")
    system_prompt = load_prompt()
    
    if not system_prompt:
        print("❌ 程序终止：无法加载 Prompt，请检查 prompt_template.txt 文件。")
        return

    print(f"✅ Prompt 加载成功 (长度: {len(system_prompt)} 字符)")

    # --- 2. 读取 CSV 文件 ---
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误：找不到文件 {INPUT_FILE}，请确认文件在当前目录下。")
        return

    print(f"正在读取数据文件: {INPUT_FILE} ...")
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except UnicodeDecodeError:
        print("⚠️ UTF-8 读取失败，尝试使用 GBK 编码读取...")
        df = pd.read_csv(INPUT_FILE, encoding='gbk')

    # 检查列名
    target_column = 'input_text' # ⚠️ 请确认你的CSV里这一列叫 input_text
    if target_column not in df.columns:
        print(f"❌ 错误：CSV文件中找不到列名 '{target_column}'。")
        print(f"现有列名: {list(df.columns)}")
        return

    rows=31 # 要处理的行数，测试时可以改小一些
    total_rows = len(df)
    df = df.head(rows)
    #total_rows = len(df)
    print(f"✅ 成功加载 {rows} 条数据，开始批量翻译...")
    print("-" * 50)

    # --- 3. 准备存储结果的列表 ---
    hksl_results = []
    status_results = []

    # --- 4. 遍历每一行进行翻译 ---
    for index, row in df.iterrows():
        source_text = row[target_column]
        
        # 打印进度条
        print(f"[{index+1}/{rows}] 处理中...")
        # 如果你想看完整的原文和译文，可以这样写：
        print(f"--- 第 {index+1} 条 ---")
        print(f"原文: {text}")
        print(f"译文: {translation_text}")
        print("-" * 30)
        # 如果单元格为空，跳过
        if pd.isna(source_text) or str(source_text).strip() == "":
            hksl_results.append("")
            status_results.append("empty")
            continue

        # 调用 API (传入 system_prompt)
        res = call_translation_api(str(source_text), system_prompt)
        
        hksl_results.append(res['hksl'])
        status_results.append(res['status'])
        
        # 简单打印一下错误，方便调试
        if res['status'] != 'success' and res['status'] != 'mock_success':
             print(f"\n⚠️ 第 {index+1} 行出错: {res['hksl']}")

        # 避免请求过快
        if not MOCK_MODE:
            time.sleep(0.5) 

    print("\n" + "-" * 50)
    print("处理完成，正在保存文件...")

    # --- 5. 将结果写回 DataFrame ---
    df['hksl_output'] = hksl_results
    df['api_status'] = status_results

    # --- 6. 保存为 Excel ---
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"weather_result_{timestamp}.xlsx"
    
    try:
        df.to_excel(output_filename, index=False)
        print(f"✅ 成功！结果已保存为: {output_filename}")
    except Exception as e:
        # 如果保存Excel失败（比如没装openpyxl），尝试保存CSV
        csv_filename = f"weather_result_{timestamp}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"⚠️ 保存Excel失败 ({e})，已保存为 CSV: {csv_filename}")

if __name__ == "__main__":
    main()