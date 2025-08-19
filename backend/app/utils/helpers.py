"""
ヘルパー関数のモジュール
"""
import hashlib
import secrets
import string
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone, timedelta
import json
import uuid


def generate_random_string(length: int = 32, include_special: bool = False) -> str:
    """ランダムな文字列を生成"""
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += string.punctuation
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_uuid() -> str:
    """UUIDを生成"""
    return str(uuid.uuid4())


def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    """パスワードをハッシュ化"""
    if salt is None:
        salt = generate_random_string(16)
    
    # パスワードとソルトを結合してハッシュ化
    combined = password + salt
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    
    return {
        "hash": hashed,
        "salt": salt
    }


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """パスワードを検証"""
    expected_hash = hash_password(password, salt)["hash"]
    return hashed == expected_hash


def format_datetime(dt: Union[datetime, str], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """日時をフォーマット"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format_str)


def parse_datetime(date_string: str) -> Optional[datetime]:
    """日時文字列をパース"""
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except ValueError:
        return None


def get_time_ago(dt: datetime) -> str:
    """相対的な時間を取得（例：5分前）"""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}日前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}時間前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分前"
    else:
        return "今"


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """リストを指定サイズのチャンクに分割"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """ネストしたリストを平坦化"""
    return [item for sublist in nested_list for item in sublist]


def remove_duplicates(lst: List[Any]) -> List[Any]:
    """リストから重複を除去（順序を保持）"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """安全なJSONパース"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """安全なJSONシリアライズ"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                overwrite: bool = True) -> Dict[str, Any]:
    """辞書をマージ"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, overwrite)
        elif key not in result or overwrite:
            result[key] = value
    
    return result


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """ネストした辞書から値を取得（ドット記法）"""
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> bool:
    """ネストした辞書に値を設定（ドット記法）"""
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return True


def filter_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """辞書から指定されたキーのみを抽出"""
    return {key: value for key, value in data.items() if key in allowed_keys}


def exclude_dict(data: Dict[str, Any], excluded_keys: List[str]) -> Dict[str, Any]:
    """辞書から指定されたキーを除外"""
    return {key: value for key, value in data.items() if key not in excluded_keys}


def is_valid_email(email: str) -> bool:
    """メールアドレスの妥当性を簡易チェック"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """テキストを指定長で切り詰め"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式に変換"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"
