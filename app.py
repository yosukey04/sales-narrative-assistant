import streamlit as st
import db
import ai_logic

# ページ設定
st.set_page_config(
    page_title="営業ナラティブ・アシスタント（1人社長専用）",
    page_icon="🤝",
    layout="wide"
)

# データベースの初期化
db.init_db()

# --- セッション状態の初期化 ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# --- ログアウト関数 ---
def logout():
    st.session_state.user_id = None
    st.rerun()

# --- ログイン / 新規登録 画面 ---
if st.session_state.user_id is None:
    st.title("🤝 営業ナラティブ・アシスタント")
    st.markdown("1人社長のための、あなたの強みを引き出す営業アシスタントです。")
    
    login_tab, signup_tab = st.tabs(["ログイン", "新規登録"])
    
    with login_tab:
        st.subheader("ログイン")
        with st.form("login_form"):
            login_email = st.text_input("メールアドレス")
            login_password = st.text_input("パスワード", type="password")
            submitted = st.form_submit_button("ログイン")
            if submitted:
                user = db.authenticate_user(login_email, login_password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.success("ログインしました！")
                    st.rerun()
                else:
                    st.error("メールアドレスまたはパスワードが間違っています。")

    with signup_tab:
        st.subheader("新規登録")
        with st.form("signup_form"):
            signup_email = st.text_input("メールアドレス")
            signup_password = st.text_input("パスワード", type="password")
            
            st.markdown("---")
            st.markdown("**プライバシーポリシー（同意事項）**")
            st.markdown("- 本サービスに入力された文字起こし等のデータは、回答生成のため連携AI（OpenAI）等に送信されます。")
            st.markdown("- ただし、入力データがAIの学習（モデルの改善）に利用されることはありません。")
            agreed = st.checkbox("上記の内容およびプライバシーポリシーに同意します")
            
            signup_submitted = st.form_submit_button("アカウントを作成")
            if signup_submitted:
                if not signup_email or not signup_password:
                    st.error("メールアドレスとパスワードを入力してください。")
                elif not agreed:
                    st.error("プライバシーポリシーへの同意が必要です。")
                else:
                    success, msg = db.create_user(signup_email, signup_password, agreed)
                    if success:
                        # 登録成功後、自動ログイン
                        user = db.authenticate_user(signup_email, signup_password)
                        st.session_state.user_id = user["id"]
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
# ==========================================
# --- メインコンテンツ（ログイン後） ---
# ==========================================
else:
    # ユーザー情報の取得
    user_data = db.get_user_by_id(st.session_state.user_id)

    # --- サイドバー：ユーザープロファイル設定 ---
    with st.sidebar:
        st.header("👤 社長プロファイル設定")
        st.write(f"ログイン中: {user_data['email']}")
        if st.button("ログアウト"):
            logout()
        st.markdown("---")
        st.write("あなたの強みやビジョンをAIに共有してください。")
        
        with st.form("profile_form"):
            user_name = st.text_input("お名前", value=user_data.get("user_name", ""))
            biz_profile = st.text_area("事業内容・サービス詳細", value=user_data.get("biz_profile", ""), height=100)
            target_persona = st.text_area("ターゲット（理想の顧客像）", value=user_data.get("target_persona", ""), height=100)
            unique_value = st.text_area("独自の強み・選ばれる理由・実績", value=user_data.get("unique_value", ""), height=100)
            vision_story = st.text_area("仕事にかける想い・理念", value=user_data.get("vision_story", ""), height=100)
            
            submit_btn = st.form_submit_button("プロファイルを保存")
            if submit_btn:
                db.save_user_profile(user_data["id"], user_name, biz_profile, target_persona, unique_value, vision_story)
                st.success("プロファイルを更新しました！")
                st.rerun() # 最新の状態で再描画

    st.title("🤝 営業ナラティブ・アシスタント")
    st.markdown("""
    私はあなたの「絶対的な味方」として振る舞うAI秘書です。
    営業は「奪い合い」ではなく「価値の提供」です。あなたの強みを最大限活かし、自信を持って振る舞えるようサポートします。
    """)

    tab1, tab2, tab3 = st.tabs(["🔍 A. 10秒スカウター", "📋 B. 立ち回り指令書", "📝 C. 商談採点・反省会"])

    # CNO相談ボタンを表示するヘルパー関数
    def render_cno_button():
        st.markdown("---")
        st.info("💡 **分析結果を受けて**")
        st.markdown("より独自のナラティブ（コンセプト）をプロと磨き上げたい方はこちら")
        st.link_button("👉 CNO個別相談に申し込む", "https://example.com/cno-consulting", type="primary")

    # --- タブA: 10秒スカウター ---
    with tab1:
        st.subheader("相手リサーチ（話のきっかけ生成）")
        target_person = st.text_input("相手の「社名」または「氏名」を入力してください:")
        if st.button("リサーチ開始", key="btn_scouter") and target_person:
            with st.spinner("リサーチ中..."):
                result = ai_logic.scout_target(user_data, target_person)
                st.success("リサーチ完了！")
                st.markdown(result)
                
                # 回答直後の別UIとして相談ボタン配置
                render_cno_button()

    # --- タブB: 立ち回り指令書 ---
    with tab2:
        st.subheader("イベント戦略")
        event_info = st.text_area("参加する交流会やイベントの概要、または参加者リストを入力してください:")
        if st.button("指令書を作成", key="btn_strategy") and event_info:
            with st.spinner("分析中..."):
                result = ai_logic.generate_strategy(user_data, event_info)
                st.success("指令書作成完了！")
                st.markdown(result)
                
                # 回答直後の別UIとして相談ボタン配置
                render_cno_button()

    # --- タブC: 商談採点・反省会 ---
    with tab3:
        st.subheader("会話文字起こし分析")
        transcript = st.text_area("商談や交流会の会話文字起こしテキストを入力してください:", height=200)
        if st.button("採点と反省をする", key="btn_review") and transcript:
            with st.spinner("分析・採点中..."):
                result = ai_logic.review_meeting(user_data, transcript)
                st.success("分析完了！")
                st.markdown(result)
                
                # 回答直後の別UIとして相談ボタン配置
                render_cno_button()
