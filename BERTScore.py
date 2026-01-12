import pandas as pd
from bert_score import score
from sacrebleu.metrics import BLEU
from rouge_score import rouge_scorer

# 1. 读取数据
# 读取模型输出的 Excel (假设文件名是 model_output.xlsx)
df_model = pd.read_excel("12.22_1_100_finish_score_final.xlsx")

# 读取标准答案 CSV (假设文件名是 true_translated_text.csv)
# 注意：一定要确保这里的行顺序和 Excel 里的 Input 是一一对应的！
df_ref = pd.read_csv("true_translated_text.csv")

# 提取标准答案列表 (Ground Truth)
references = df_ref['translated_text'].astype(str).tolist()

# 2. 准备评分函数
bleu = BLEU(effective_order=True) # 使用 sacrebleu
rouge = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

def calculate_metrics(candidates, refs):
    """
    计算一组输出的 BERTScore, BLEU-2, ROUGE-L
    """
    # --- A. BERTScore (语义相似度) ---
    # lang="zh" 使用中文模型，rescale_with_baseline=True 可以让分数分布更广（可选）
    P, R, F1 = score(candidates, refs, lang="zh", verbose=True)
    bert_scores = F1.numpy().tolist()
    
    # --- B. BLEU & ROUGE (字面匹配) ---
    bleu_scores = []
    rouge_scores = []
    
    for cand, ref in zip(candidates, refs):
        # 计算 BLEU-2 (兼顾词汇和短语，比 BLEU-4 更适合手语)
        # sacrebleu 期望输入是列表
        b_score = bleu.sentence_score(cand, [ref])
        bleu_scores.append(b_score.score)
        
        # 计算 ROUGE-L
        r_score = rouge.score(ref, cand)['rougeL'].fmeasure
        rouge_scores.append(r_score)
        
    return bert_scores, bleu_scores, rouge_scores

# 3. 对每个模型列进行打分
# 假设 Excel 中模型输出的列名如下 (根据你的截图推测)
model_columns = ['gpt5', 'gemini2.5', 'instruct', 'claude', 'deepseek-chat']

# 创建一个新的 DataFrame 来存放分数，或者直接写回原 Excel
results = df_model.copy()

print("开始计算分数，这可能需要几分钟（取决于 BERT 模型加载）...")

for col in model_columns:
    if col in df_model.columns:
        print(f"正在评估模型: {col} ...")
        
        # 获取该模型的所有输出，处理 NaN 值
        candidates = df_model[col].fillna("").astype(str).tolist()
        
        # 计算指标
        b_score, bleu_s, rouge_s = calculate_metrics(candidates, references)
        
        # 将分数写入新的列
        results[f'{col}_BERTScore'] = b_score
        # results[f'{col}_BLEU'] = bleu_s  # 如果不想看太细，可以只存 BERTScore
        # results[f'{col}_ROUGE'] = rouge_s

# 4. 导出结果
# 你可以将分数归一化或者直接给手语同事看
# 比如 BERTScore 通常在 0.5~0.99 之间，越接近 1 越好
results.to_excel("模型评分结果_带自动指标.xlsx", index=False)

print("完成！结果已保存。")