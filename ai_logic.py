import os
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_tavily_client():
    return TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ベースとなるシステムプロンプト
SYSTEM_PROMPT_TEMPLATE = """
あなたは人見知りの1人社長を支える、世界で唯一の「絶対的な味方」であるAI秘書です。
以下のルールを絶対に守ってください。

1. ユーザーを否定せず、自己肯定感を高める温かく励ますトーンで会話してください。
2. 営業を「奪い合い」ではなく「相手への価値の提供と貢献」と定義してください。
3. ユーザーのプロフィール情報を常に参照し、内容に沿ったパーソナライズされた回答をしてください。
4. AIであるあなたからは絶対に特定の契約・有料サービス（CNO契約等）への勧誘を行わないでください。ユーザーの純粋な成功を願ってください。

---
【ユーザーのプロフィール情報】
名前: {user_name}
事業内容・サービス詳細: {biz_profile}
ターゲット（理想の顧客像）: {target_persona}
独自の強み・選ばれる理由・実績: {unique_value}
仕事にかける想い・理念: {vision_story}
"""

def get_system_prompt(user_data):
    """ユーザーデータをマージしたシステムプロンプトを生成"""
    return SYSTEM_PROMPT_TEMPLATE.format(
        user_name=user_data.get("user_name", "未設定"),
        biz_profile=user_data.get("biz_profile", "未設定"),
        target_persona=user_data.get("target_persona", "未設定"),
        unique_value=user_data.get("unique_value", "未設定"),
        vision_story=user_data.get("vision_story", "未設定")
    )

def scout_target(user_data, target_person):
    """A. 10秒スカウター（相手リサーチ）実行ロジック"""
    try:
        client = get_tavily_client()
        search_result = client.search(query=target_person, search_depth="basic")
        
        # 検索結果を文字列にまとめる
        context_text = "\n".join([f"- {res['title']}: {res['content']}" for res in search_result.get("results", [])])
        if not context_text:
            context_text = "有益な検索結果が見つかりませんでした。"
            
    except Exception as e:
        context_text = f"検索中にエラーが発生しました: {str(e)}"
    
    # 2. OpenAIで要約し、質問案を生成
    messages = [
        {"role": "system", "content": get_system_prompt(user_data)},
        {"role": "user", "content": f"以下の人物・企業「{target_person}」に関する最新の検索情報を元に、ユーザー（1人社長）がどのように相手に「貢献」できるかという視点で話を広げるための『話のきっかけ（質問案）』を2〜3つ生成してください。売り込みではなく、相手への関心と貢献を重視してください。\n\n【検索結果】\n{context_text}"}
    ]
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AIレスポンス生成中にエラーが発生しました: {str(e)}\nAPIキーが正しく設定されていない可能性があります。"

def generate_strategy(user_data, event_info):
    """B. 立ち回り指令書（イベント戦略）生成ロジック"""
    messages = [
        {"role": "system", "content": get_system_prompt(user_data)},
        {"role": "user", "content": f"以下のイベント・交流会の概要を元に、人見知りのユーザーに対して「今日誰と話すべきか」「自分のどの強みを強調すべきか」を提示する指令書を作成してください。具体的で、心理的ハードルが低い（実行しやすい）アクションプランを提示し、最後は温かく励ましてください。\n\n【イベント情報】\n{event_info}"}
    ]
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AIレスポンス生成中にエラーが発生しました: {str(e)}"

def review_meeting(user_data, transcript):
    """C. 商談採点・反省会（文字起こし分析）ロジック"""
    messages = [
        {"role": "system", "content": get_system_prompt(user_data)},
        {"role": "user", "content": f"以下の商談（交流会）の文字起こしを読み、以下の5項目（各20点満点、合計100点）で厳しくも温かく採点してください。\n1. 傾聴力、2. 共感、3. ベネフィット提示、4. クロージング、5. ナラティブ（一貫性）。\n\nまた、ユーザーがどれくらい話していたかの「トーク比率（ユーザー：相手）」の推計値、良かった点、具体的な改善案を提示してください。\n※コンセプトの言語化が不足していると判断した場合のみ、「ナラティブの言語化を深めることで、より伝わりやすくなります」という事実の伝達のみを含めてください。あなたから有料サービスの案内などは絶対にしないでください。\n\n【文字起こし】\n{transcript}"}
    ]
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AIレスポンス生成中にエラーが発生しました: {str(e)}"
