import requests
import json

# 接口地址
url = "http://127.0.0.1:5000/api/translate"

# 模拟前端发送的数据
payload = {
    "text": "直至下午5時，錄得氣溫30度。"
}

print(f"📤 正在发送请求: {payload['text']} ...")

try:
    # 发送 POST 请求
    response = requests.post(url, json=payload)
    
    # 打印状态码
    print(f"状态码: {response.status_code}")
    
    # 打印返回的 JSON 数据
    if response.status_code == 200:
        print("✅ 返回结果:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("❌ 错误信息:", response.text)

except Exception as e:
    print(f"无法连接服务器: {e}")