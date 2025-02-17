import streamlit as st
import os
import tiktoken
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#models
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv


# Streamlit CloudシークレットからOPENAI_API_KEYを取得
openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]

# ChatOpenAI のインスタンスを作成
model_instance = ChatOpenAI(
    temperature=temperature, 
    model_name=model_name, 
    openai_api_key=openai_api_key  # APIキーを渡す
)

if not openai_api_key:
    st.error("🔑 OPENAI_API_KEY が設定されていません。")

MODEL_PRICES = {
    "input": {
        "gpt-3.5-turbo": 0.5 / 1_000_000,
        "gpt-4o": 5 / 1_000_000,
        "claude-3-5-sonnet-20240620": 3 / 1_000_000,
        "gemini-1.5-pro-latest": 3.5 / 1_000_000
    },
    "output": {
        "gpt-3.5-turbo": 1.5 / 1_000_000,
        "gpt-4o": 15 / 1_000_000,
        "claude-3-5-sonnet-20240620": 15 / 1_000_000,
        "gemini-1.5-pro-latest": 10.5 / 1_000_000
    }
}

def init_sidebar():
    st.sidebar.title("")

    # 🔹 **プロジェクトごとのページを選択**
    page = st.sidebar.selectbox("📂 プロジェクトを選択:", ["Home", "プロジェクト1", "プロジェクト2", "プロジェクト3"])
    # 会話履歴クリアボタン
    if st.sidebar.button("🗑 Clear Conversation"):
        st.session_state.message_history = [("system", "ALTAM is a helpful assistant.")]

    # モデル選択
    models = ("GPT-3.5", "GPT-4", "Claude 3.5 Sonnet", "Gemini 1.5 Pro")
    model = st.sidebar.radio("🤖 Choose a model:", models)

    # Temperature スライダー
    temperature = st.sidebar.slider("Temperature:", 0.0, 2.0, 0.0, 0.01)
  
    model_instance = None  # 初期値
    if model == "GPT-3.5":
        st.session_state.model_name = "gpt-3.5-turbo"
        model_instance = ChatOpenAI(temperature=temperature, model_name=st.session_state.model_name)
    elif model == "GPT-4":
        st.session_state.model_name = "gpt-4o"
        model_instance = ChatOpenAI(temperature=temperature, model_name=st.session_state.model_name)
    elif model == "Claude 3.5 Sonnet":
        st.session_state.model_name = "claude-3-5-sonnet-20240620"
        model_instance = ChatAnthropic(temperature=temperature, model_name=st.session_state.model_name)
    elif model == "Gemini 1.5 Pro":
        st.session_state.model_name = "gemini-1.5-pro-latest"
        model_instance = ChatGoogleGenerativeAI(temperature=temperature, model=st.session_state.model_name)
    return model_instance, page  # 必ず page も返す


def load_project_data(project_name):
    #"""プロジェクトごとに異なるデータをロード"""
    #    project_files = {
    #"プロジェクト1": "data/financial_report.pdf",
    #"プロジェクト2": "data/medical_paper.csv",
    #"プロジェクト3": "data/python_tutorial.md"
    #}
    # # プロジェクトに対応するファイルを取得
    #data_file = project_files.get(project_name, None)
     # `st.session_state` にデータを保存（ファイルのパス or データ内容）
    #if data_file:
        #with open(data_file, "r", encoding="utf-8") as f:
    #        st.session_state.project_data = f.read()
    #else:
    #    st.session_state.project_data = "このプロジェクトには特定の資料が設定されていません。"
    #return data_file

    if project_name == "プロジェクト1":
        return "データ1: 金融レポート"
    elif project_name == "プロジェクト2":
        return "データ2: 医療論文"
    elif project_name == "プロジェクト3":
        return "データ3: Pythonチュートリアル"
    return "デフォルトデータ"


def main():

    st.set_page_config(
        page_title="I am ALTAMGPT",
        page_icon="🤖"
    )

     #サイドバーを初期化（モデル + ページ選択）
    st.session_state.llm, page = init_sidebar()
 
    
      #ページごとの表示処理
    if page == "Home":
        st.header("🏠 Home - ALTAM SOFTWARE OF LLM")
        st.write("Welcome to ALTAMGPT! プロジェクトをサイドバーで選択してください。")
        return
    
        #プロジェクトデータを取得
    project_data = load_project_data(page)
        #プロジェクトごとのデータを明示
    st.write(f"このプロジェクトでは **{project_data}** を使用します。")
  
     # CSSを適用（背景色変更 & サイドバーのデザイン）**
    st.markdown(
        """
    <style>
    /* ページ全体の背景 */
    body {
        background-color: #e0f7fa; /* 薄い水色 */
    }

    /* サイドバーの背景を黒に変更 */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E !important;  /* ダークグレー（黒に近い） */
        color: white !important;  /* 文字色を白に */
    }

    /*サイドバー内のすべてのテキストを白に変更する*/
    section[data-testid="stSidebar"] button {
        background-color: #333 !important;  /* ボタンをグレー */
        color: white !important;  /* ボタンの文字色を白 */
        border: 1px solid #555 !important;  /* 枠線を暗めのグレー */
    }

    /* サイドバー内のボタンのデザイン変更 */
    [data-testid="stSidebar"] button {
        background-color: #333 !important;  /* ボタンをグレー */
        color: white !important;  /* ボタンの文字色を白 */
        border: 1px solid #555 !important;  /* 枠線を暗めのグレー */
    }

    /* サイドバーのスライダー（Temperature）カスタマイズ */
    [data-testid="stSidebar"] .stSlider {
        color: white !important;
    }

    /* サイドバーのラジオボタン（モデル選択） */
    [data-testid="stSidebar"] label {
        color: white !important; /* ラベルの文字色を白 */
    }
    </style>
    """,
    unsafe_allow_html=True
)


    # ページごとの表示処理**
    if page == "Home":
        st.header("🏠 Home - ALTAM SOFTWARE OF LLM")
        st.write("Welcome to ALTAMGPT! プロジェクトをサイドバーで選択してください。")
        return  # Homeではチャット機能なし

     # Home 以外のページでチャット機能を表示**
    st.header(f"📂 {page}")
    chat_interface()

 


def chat_interface():

    # チャット履歴の初期化: message_history がなければ作成
    if "message_history" not in st.session_state:
        st.session_state["message_history"] = [
            # System Prompt を設定 ('system' はSystem Promptを意味する)
            ("system", "ALTAM is a helpful assistant.")
        ]

    # ChatGPTに質問を与えて回答を取り出す(パースする)処理を作成 (1.-4.の処理)
    # 1. ChatGPTのモデルを呼び出すように設定
    #    (デフォルトではGPT-3.5 Turboが呼ばれる)
    llm = st.session_state.llm


    # 2. ユーザーの質問を受け取り、ChatGPTに渡すためのテンプレートを作成
    #    テンプレートには過去のチャット履歴を含めるように設定

    N = 3 #直近3つのメッセージだけをAPIに送る。

    prompt = ChatPromptTemplate.from_messages([
        *st.session_state["message_history"][-N:],#最新のもののみ表示する。
        ("user", "{user_input}")  # ここにあとでユーザーの入力が入る
    ])


    # 3. ChatGPTの返答をパースするための処理を呼び出し
    output_parser = StrOutputParser()


    # 4. ユーザーの質問をChatGPTに渡し、返答を取り出す連続的な処理(chain)を作成
    #    各要素を | (パイプ) でつなげて連続的な処理を作成するのがLCELの特徴
    chain = prompt | llm | output_parser

     #入力の部分をテキストボックスに変更しました。
    container = st.container()
    with container:
        with st.form(key="myform", clear_on_submit=True):
            user_input = st.text_area(label="Message:", key="input", height=100)
            submit_button = st.form_submit_button(label = "Send")

            if submit_button and user_input:
                #入力されてボタンを押されたら実行

                with st.spinner("ChatGPT is typing ..."):
                    response = chain.invoke({"user_input": user_input})

                # ユーザーの質問を履歴に追加 ('user' はユーザーの質問を意味する)
                st.session_state.message_history.append(("user", user_input))

            # ChatGPTの回答を履歴に追加 ('assistant' はChatGPTの回答を意味する)
                st.session_state.message_history.append(("ai", response))

      # 最新のメッセージのみ表示（rerun なしで即時反映）
        if "last_message" in st.session_state:
           with st.chat_message("assistant"):
                st.markdown(st.session_state["last_message"])

    with st.spinner("ChatGPT is trying"):
        response = chain.invoke({"user_input": user_input})

    # チャット履歴の表示
    for role, message in st.session_state.get("message_history", []):
        with st.chat_message(role):
            st.markdown(message)


if __name__ == '__main__':
    main()
