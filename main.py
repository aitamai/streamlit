import streamlit as st
import os
import streamlit as st
import requests

# GitHub シークレット or Streamlit secrets から API キーを取得
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ChatGPT & Groq の APIエンドポイント
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="Chatbot (GPT-3.5-Turbo & Groq)", page_icon="🤖",layout="wide")

# モデルの価格リスト
MODEL_PRICES = {
    "input": {
        "gpt-3.5-turbo": 0.5 / 1_000_000,
        "mixtral-8x7b-32768": 3 / 1_000_000
    },
    "output": {
        "gpt-3.5-turbo": 1.5 / 1_000_000,
        "mixtral-8x7b-32768": 15 / 1_000_000
    }
}

# チャット履歴の初期化
if "message_history" not in st.session_state:
    st.session_state.message_history = [("system", "ALTAM is a helpful assistant.")]

# 🔹 **AIエンジンを切り替え**
def chat_with_ai(user_input, model_instance, temperature):
    """GPT-3.5-Turbo または Groq (Mixtral) で応答を生成"""

    if not model_instance:
        return "⚠️ モデルが正しく選択されていません。"

    # 直近の履歴 N 件のみを送信
    N = 3  
    messages = [{"role": role, "content": content} for role, content in st.session_state.message_history[-N:]]
    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": model_instance["model_name"],
        "messages": messages,
        "max_tokens": 200,
        "temperature": temperature
    }

    headers = {
        "Authorization": f"Bearer {model_instance['api_key']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(model_instance["api_url"], headers=headers, json=payload)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる

        ai_response = response.json()["choices"][0]["message"]["content"].strip()

        # 会話履歴に追加
        st.session_state.message_history.append(("user", user_input))
        st.session_state.message_history.append(("assistant", ai_response))

        return ai_response

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ APIリクエストエラー: {e}")  # エラーをStreamlitのUIに表示
        return f"⚠️ APIリクエストエラー: {e}"


# 🔹 **サイドバーの設定**
def init_sidebar():
    st.sidebar.title("チャットボット")

    # 🔹 **プロジェクトを選択**
    page = st.sidebar.selectbox("📂 プロジェクトを選択:", ["Home", "金融調査員", "医者", "プロエンジニア"])

    # 会話履歴クリアボタン
    if st.sidebar.button("🗑 会話履歴のリセット"):
        st.session_state.message_history = [("system", "ALTAM is a helpful assistant.")]

    # モデル選択
    models = ["GPT-3.5-Turbo", "Groq (Mixtral)"]
    model = st.sidebar.radio("🤖 モデルを選択:", models)

    # Temperature スライダー
    temperature = st.sidebar.slider("Temperature:", 0.0, 2.0, 0.7, 0.01)

    # モデルインスタンスの設定
    model_instance = {
        "GPT-3.5-Turbo": {
            "api_url": OPENAI_URL,
            "api_key": OPENAI_API_KEY,
            "model_name": "gpt-3.5-turbo"
        },
        "Groq (Mixtral)": {
            "api_url": GROQ_URL,
            "api_key": GROQ_API_KEY,
            "model_name": "mixtral-8x7b-32768"
        }
    }.get(model, None)


    return model_instance, page, temperature

# 🔹 **プロジェクトデータのロード**
def load_project_data(project_name):
    project_data = {
        "金融調査員": "データ1: 金融レポート",
        "医者": "データ2: 医療論文",
        "エンジニア": "データ3: Pythonチュートリアル"
    }
    return project_data.get(project_name, "エンジニアファイル")

# 🔹 **チャットインターフェース**
def chat_interface(model_instance, temperature):
    """Streamlit のチャットUIを提供"""

    st.title("💬 チャットボット")

    # チャット履歴の表示
    chat_log = ""
    for role, message in st.session_state.message_history:
        if role == "user":
            chat_log += f"👤 **ユーザー**: {message}\n\n"
        elif role == "assistant":
            chat_log += f"🤖 **AI**: {message}\n\n"

    # チャットログを表示
    st.markdown(f"```markdown\n{chat_log}\n```")

    # ユーザー入力
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("メッセージを入力してください:", key="input", height=100)
        submit_button = st.form_submit_button(label="送信")

    if submit_button and user_input:
        with st.spinner("考え中..."):
            ai_response = chat_with_ai(user_input, model_instance, temperature)

        # 画面を更新してチャット履歴を反映
        st.rerun()  # ここを修正！


                  
# 🔹 **メイン関数**
def main():

    # サイドバーの初期化
    model_instance, page, temperature = init_sidebar()

    # プロジェクトごとのデータを取得
    project_data = load_project_data(page)

    # ページの表示処理
    if page == "Home":
        st.header("🏠 Home - ALTAM SOFTWARE OF LLM")
        st.write("Welcome to ALTAMGPT! プロジェクトをサイドバーで選択してください。")
        return

    # プロジェクトごとのデータを明示
    st.header(f"📂 {page}")
    st.write(f"このプロジェクトでは **{project_data}** を使用します。")

     # CSSを適用（背景色変更 & サイドバーのデザイン）**
    st.markdown(
    """
    <style>

     /* 🔥 ヘッダー（Streamlit ツールバー）を非表示 */
    header, [data-testid="stToolbar"], [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* 📝 フッターを非表示 */
    footer, [data-testid="stFooter"], .st-emotion-cache-1wmy9hl {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* 📌 スマホ画面でのレイアウト調整 */
    @media (max-width: 768px) {
        header, footer, [data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="stFooter"], .st-emotion-cache-1wmy9hl {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }
    }
     
    /* 🌟 全体の背景 */
    body {
        background-color: #f4f7f9; /* 落ち着いたブルーグレー */
        color: #333; /* 文字をダークグレー */
        font-family: 'Arial', sans-serif;
    }

    /* 🟦 サイドバーのデザイン */
    [data-testid="stSidebar"] {
        background-color: #1e1e2f !important;  /* 濃いネイビーブルー */
        color: white !important; /* テキストを白に */
    }

    /* サイドバー内のボタンデザイン */
    [data-testid="stSidebar"] button {
        background-color: #4a4a7d !important;  /* ネイビーブルー */
        color: white !important;  
        border: 1px solid #6b6b9d !important;
        transition: background-color 0.3s ease;
    }

    /* ホバー時のボタンカラー変更 */
    [data-testid="stSidebar"] button:hover {
        background-color: #5a5a8d !important; 
    }

    /* 🔥 入力エリアのデザイン変更 */
    textarea {
        background-color: #ffffff !important;
        border: 2px solid #6b6b9d !important;
        border-radius: 8px;
        color: #333 !important;
        padding: 10px;
        font-size: 14px;
    }

    /* すべてのラジオボタンをグレー */
    [data-testid="stSidebar"] label {
        color: gray !important;
        font-weight: normal;
    }

    /* 選択されたラジオボタンのラベルを白くする */
    [data-testid="stSidebar"] input:checked + div {
        color: white !important;
        font-weight: bold;
    }


    /* 💬 チャット履歴のデザイン */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
    }

    /* 🎨 チャット履歴内の各メッセージ */
    .chat-message {
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 8px;
        font-size: 14px;
    }

    /* ユーザーのメッセージ */
    .user-message {
        background-color: #cce5ff;
        border-left: 5px solid #007bff;
    }

    /* AI のメッセージ */
    .ai-message {
        background-color: #e6e6e6;
        border-left: 5px solid #6c757d;
    }

    /* 🔘 スライダーのデザイン */
    [data-testid="stSidebar"] .stSlider {
        color: white !important;
    }

    /* 📌 ラジオボタンのデザイン */
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: bold;
    }

    /* サイドバーのタイトルを白くする */
    [data-testid="stSidebar"] h1 {
        color: white !important;
    }

    /* 📱 レスポンシブデザイン */
    @media (max-width: 768px) {
        body {
            font-size: 14px;
        }
        .chat-container {
            max-height: 300px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
        
    # チャットインターフェースを表示
    chat_interface(model_instance, temperature)

if __name__ == '__main__':
    main()
