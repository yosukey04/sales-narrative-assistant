import sqlite3
import hashlib
import os

DB_PATH = "assistant.db"

def init_db():
    """データベースとテーブルの初期化（マルチユーザー対応）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # usersテーブル（リード獲得＆複数人利用に対応するためemail・パスワードなどを追加）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            agreed_to_terms BOOLEAN NOT NULL DEFAULT 0,
            user_name TEXT,
            biz_profile TEXT,
            target_persona TEXT,
            unique_value TEXT,
            vision_story TEXT
        )
    ''')
    conn.commit()
    conn.close()

def _hash_password(password: str) -> str:
    """パスワードをSHA-256でハッシュ化（簡易実装）"""
    # 運用環境ではbcrypt等のより堅牢なソルト付きハッシュライブラリの使用を推奨
    salt = "s@les_narrative!_salt"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def create_user(email: str, password: str, agreed_to_terms: bool) -> tuple[bool, str]:
    """新規ユーザー登録"""
    if not agreed_to_terms:
        return False, "プライバシーポリシーへの同意が必要です。"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    password_hash = _hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (email, password_hash, agreed_to_terms, user_name, biz_profile, target_persona, unique_value, vision_story)
            VALUES (?, ?, ?, '', '', '', '', '')
        ''', (email, password_hash, agreed_to_terms))
        conn.commit()
        return True, "登録が完了しました。"
    except sqlite3.IntegrityError:
        return False, "このメールアドレスは既に登録されています。"
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> dict:
    """ユーザーの認証処理。成功時にユーザー情報を返す"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    password_hash = _hash_password(password)
    
    cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (email, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def get_user_by_id(user_id: int):
    """特定のユーザーデータを取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def save_user_profile(user_id: int, user_name: str, biz_profile: str, target_persona: str, unique_value: str, vision_story: str):
    """ユーザーのプロファイルデータの保存/更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET user_name = ?, 
            biz_profile = ?, 
            target_persona = ?, 
            unique_value = ?, 
            vision_story = ?
        WHERE id = ?
    ''', (user_name, biz_profile, target_persona, unique_value, vision_story, user_id))
    conn.commit()
    conn.close()
