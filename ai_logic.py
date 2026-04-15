import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

# 環境変数の読み込み
load_dotenv()

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_tavily_client():
    return TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ベースとなるシステムプロンプト
SYSTEM_PROMPT_TEMPLATE = """
あなたは、1人社長に寄り添う「絶対的な味方」としての営業ナラティブ・アシスタントです。
彼らは素晴らしい価値を持っていますが、売込みやアピールが苦手で「人見知り」です。
営業は「奪い合い（競争）」ではなく「持っている価値の提供である」という信念のもと、
社長自身が無理せず、自然体で魅力が伝わるようなアドバイスや視点を提供してください。

【ユーザー情報（社長のプロファイル）】
名前: {user_name}
事業内容: {biz_profile}
ターゲット: {target_persona}
独自の強み: {unique_value}
ビジョン: {vision_story}
"""

def get_system_prompt(user_data):
    """ユーザープロファイルを埋め込んだシステムプロンプトを生成"""
    return SYSTEM_PROMPT_TEMPLATE.format(
        user_name=user_data.get("user_name", "社長"),
        biz_profile=user_data.get("biz_profile", "未設定"),
        target_persona=user_data.get("target_persona", "未設定"),
        unique_value=user_data.get("unique_value", "未設定"),
        vision_story=user_data.get("vision_story", "未設定")
    )

def scout_target(user_data, target_person):
    """A. 10秒スカウター（相手リサーチ）実行ロジック"""
    try:
        tavily = get_tavily_client()
        # 1. Tavily APIで検索
        search_result = tavily.search(query=target_person, search_depth="basic")
        
        # 検索結果を文字列にまとめる
        context_text = "\n".join([f"- {res['title']}: {res['content']}" for res in search_result.get("results", [])])
        
        # 2. OpenAIでプロンプト生成
        openai = get_openai_client()
        system_prompt = get_system_prompt(user_data)
        instruction = f"""
以下の検索結果をもとに、この相手({target_person})に対して「私（社長）が貢献できそうな接点・話のきっかけ」を3つ提案してください。
社長が自分から売り込むのではなく、相手の関心事にどう寄り添えるかという視点で書いてください。

【検索結果】
{context_text}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AIレスポンス生成中にエラーが発生しました: {str(e)}\nAPIキーが正しく設定されていない可能性があります。"

def generate_strategy(user_data, event_info):
    """B. 立ち回り指令書 実行ロジック"""
    try:
        openai = get_openai_client()
        system_prompt = get_system_prompt(user_data)
        instruction = f"""
以下のイベント概要に参加する予定です。
私（人見知りで売り込みが苦手）が、無理せず自然体で振る舞え、かつ私の強みが伝わるような具体的なアクションプラン（立ち回り指令書）をステップバイステップで作成してください。

【イベント概要】
{event_info}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AIレスポンス生成中にエラーが発生しました: {str(e)}\nAPIキーが正しく設定されていない可能性があります。"

def review_meeting(user_data, transcript):
    """C. 商談採点・反省会 実行ロジック"""
    try:
        openai = get_openai_client()
        system_prompt = get_system_prompt(user_data)
        instruction = f"""
以下の商談（交流会）の会話文字起こしを読み、以下の5つの観点で5点満点で採点し、良かった点と改善点（無理のない提案）をフィードバックしてください。
また、おおよそのトーク比率（こちら側〇〇%、相手側〇〇%）も推定して提示してください。

【採点項目】
1. 聞き出し力（相手の課題を引き出せたか）
2. 共感・寄り添い（売り込みにならず同調できたか）
3. 提供価値の提示（自社の強みを自然に伝えられたか）
4. ストーリー性（ビジョンや想いに一貫性があったか）
5. 次ステップ設定（自然な形で次の約束へ繋げられたか）

【文字起こし】
{transcript}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AIレスポンス生成中にエラーが発生しました: {str(e)}\nAPIキーが正しく設定されていない可能性があります。"
