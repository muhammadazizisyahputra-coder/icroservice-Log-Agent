import os
import glob
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载配置（API Key 等）
load_dotenv()

# 2. 【核心黑科技】全自动寻找 SKILL.md
# 无论文件夹叫 xiaomei 还是 小美，只要文件在，它就能搜到
print("🔍 正在扫描人格文件，请稍后...")
found_files = glob.glob("personalities/**/SKILL.md", recursive=True)

# 备选方案：如果找不到 SKILL.md，就找 persona.md
if not found_files:
    found_files = glob.glob("personalities/**/persona.md", recursive=True)

if not found_files:
    print("❌ 报错：在 personalities 文件夹里完全找不到任何性格定义文件！")
    print("请确认：1. 你运行过 demo.py  2. 当前目录下确实有 personalities 文件夹")
    # 帮你打印一下当前目录下的东西，方便排查
    print(f"当前运行目录: {os.getcwd()}")
    print(f"目录下内容: {os.listdir('.')}")
    exit()

# 选出找到的第一个文件
target_path = found_files[0]
print(f"✅ 成功对接灵魂文件: {target_path}")

with open(target_path, "r", encoding="utf-8") as f:
    personality_content = f.read()

# 3. 配置 Mimo 接口
client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY"),
    base_url=os.getenv("MIMO_BASE_URL")
)

print("\n" + "="*40)
print("✨ AI 人格已激活！你可以开始对话了")
print("提示：输入 'quit' 或 '退出' 结束对话")
print("="*40 + "\n")

# 初始化记忆
messages = [{"role": "system", "content": personality_content}]

while True:
    user_input = input("【我】: ")

    if user_input.lower() in ['quit', 'exit', '退出']:
        print("再见，期待下次见面。")
        break

    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})

    try:
        # 呼叫 Mimo API 生成回复
        response = client.chat.completions.create(
            model=os.getenv("MIMO_MODEL"),
            messages=messages,
            temperature=0.8
        )

        reply = response.choices[0].message.content
        print(f"\n【AI】: {reply}\n")

        # 存入对话历史
        messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        print(f"\n❌ 对话过程中出错了: {e}")