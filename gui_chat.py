import streamlit as st
import os
import glob
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

# 1. 网页基础设置 (UI 风格更中性，适合所有类型的人格)
st.set_page_config(page_title="Renge Engine | 人格模拟引擎", page_icon="🧠", layout="wide")
load_dotenv()

# --- 核心函数：全自动路径雷达 ---
def scan_for_renge():
    # 扫描目录下所有的人格定义文件
    files = glob.glob("**/SKILL.md", recursive=True)
    if not files:
        files = glob.glob("**/persona.md", recursive=True)
    return files

# --- 侧边栏：人格炼制中心 ---
with st.sidebar:
    st.title("🧪 人格炼制 (Renge Lab)")
    st.write("上传资料，定制你的数字生命")

    # A. 资料上传
    uploaded_file = st.file_uploader("上传聊天记录/语料 (.txt)", type=["txt"])
    # 允许用户自定义人格标识符，默认建议以 renge_ 开头
    renge_slug = st.text_input("给这个人格命名 (如: renge_ex, renge_friend):", "renge_1")

    if st.button("🚀 开始炼制灵魂"):
        if uploaded_file and renge_slug:
            temp_path = f"raw_{renge_slug}.txt"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.info(f"正在分析语料并蒸馏人格 '{renge_slug}'...")

            try:
                # 自动调用后台的炼制脚本
                cmd = f"python demo.py --file {temp_path} --slug {renge_slug}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode == 0:
                    st.success(f"✨ 炼制成功！'{renge_slug}' 已加入角色库。")
                    if os.path.exists(temp_path): os.remove(temp_path)
                else:
                    st.error(f"炼制失败：{result.stderr}")
            except Exception as e:
                st.error(f"运行出错：{e}")
        else:
            st.warning("请确认已上传文件并填写了名字。")

    st.markdown("---")

    # B. 角色切换
    st.title("🎭 角色库")
    all_renge = scan_for_renge()

    if all_renge:
        # 提取文件夹名称作为角色名
        renge_map = {os.path.basename(os.path.dirname(p)): p for p in all_renge}
        selected_renge = st.selectbox("当前加载的人格：", list(renge_map.keys()))
        target_path = renge_map[selected_renge]

        with open(target_path, "r", encoding="utf-8") as f:
            renge_skill = f.read()
        st.success(f"已进入状态：{selected_renge}")
    else:
        st.warning("目前没有检测到人格文件。")
        st.stop()

    if st.button("🗑️ 开启新话题"):
        st.session_state.messages = []
        st.rerun()

# 2. 初始化 API 客户端
client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY"),
    base_url=os.getenv("MIMO_BASE_URL")
)

# 3. 初始化对话历史 (加入人格约束)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": renge_skill}]

# 4. 渲染界面
st.title(f"💬 正在与 '{selected_renge}' 对话")
st.caption("基于 Mimo 2.5 Pro 引擎驱动的人格模拟")

# 展示聊天气泡
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "👤" if message["role"] == "user" else "🧠"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# 5. 聊天输入
if prompt := st.chat_input("发送消息..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🧠"):
        placeholder = st.empty()
        full_res = ""
        try:
            response = client.chat.completions.create(
                model=os.getenv("MIMO_MODEL"),
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in response:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        full_res += delta.content
                        placeholder.markdown(full_res + "▌")

            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"对话引擎响应异常: {e}")