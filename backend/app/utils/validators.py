"""
バリデーション関数のモジュール
"""
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError


def validate_email_format(email: str) -> bool:
    """メールアドレスの形式を検証"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_password_strength(password: str) -> Dict[str, Any]:
    """パスワードの強度を検証"""
    result = {
        "is_valid": True,
        "errors": [],
        "score": 0
    }
    
    if len(password) < 8:
        result["errors"].append("パスワードは8文字以上である必要があります")
        result["is_valid"] = False
    
    if not re.search(r"[A-Z]", password):
        result["errors"].append("大文字を含む必要があります")
        result["score"] += 1
    
    if not re.search(r"[a-z]", password):
        result["errors"].append("小文字を含む必要があります")
        result["score"] += 1
    
    if not re.search(r"\d", password):
        result["errors"].append("数字を含む必要があります")
        result["score"] += 1
    
    # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #     result["errors"].append("特殊文字を含む必要があります")
    #     result["score"] += 1
    
    if result["score"] >= 3:
        result["is_valid"] = True
    
    return result


def validate_phone_number(phone: str) -> bool:
    """電話番号の形式を検証（日本）"""
    # 日本の電話番号パターン
    pattern = r'^(\+81|0)[0-9]{9,10}$'
    return bool(re.match(pattern, phone))


def validate_date_range(start_date: Union[str, date, datetime], 
                       end_date: Union[str, date, datetime]) -> bool:
    """日付範囲の妥当性を検証"""
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        return start_date <= end_date
    except (ValueError, TypeError):
        return False


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """ファイルサイズの妥当性を検証"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """ファイル拡張子の妥当性を検証"""
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_ext in allowed_extensions


def validate_json_schema(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """JSONスキーマの妥当性を検証"""
    result = {
        "is_valid": True,
        "errors": [],
        "missing_fields": []
    }
    
    for field in required_fields:
        if field not in data or data[field] is None:
            result["missing_fields"].append(field)
            result["is_valid"] = False
    
    if not result["is_valid"]:
        result["errors"].append(f"必須フィールドが不足しています: {', '.join(result['missing_fields'])}")
    
    return result


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """文字列のサニタイズ"""
    if not text:
        return ""
    
    # HTMLタグを除去
    text = re.sub(r'<[^>]+>', '', text)
    
    # 特殊文字をエスケープ
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    # 長さ制限
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def validate_url(url: str) -> bool:
    """URLの形式を検証"""
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))
