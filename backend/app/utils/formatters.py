"""
フォーマッター関数のモジュール
"""
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date, time
import locale
import json


def format_currency(amount: float, currency: str = "JPY", locale_name: str = "ja_JP") -> str:
    """通貨をフォーマット"""
    try:
        locale.setlocale(locale.LC_ALL, locale_name)
    except locale.Error:
        # ロケールが利用できない場合は英語
        locale.setlocale(locale.LC_ALL, "en_US")
    
    if currency == "JPY":
        return f"¥{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """パーセンテージをフォーマット"""
    return f"{value:.{decimal_places}f}%"


def format_number(value: Union[int, float], decimal_places: int = 0) -> str:
    """数値をフォーマット（桁区切り）"""
    if isinstance(value, int):
        return f"{value:,}"
    else:
        return f"{value:,.{decimal_places}f}"


def format_datetime_jp(dt: Union[datetime, str], format_type: str = "full") -> str:
    """日本語形式で日時をフォーマット"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    
    if format_type == "full":
        return dt.strftime("%Y年%m月%d日 %H時%M分")
    elif format_type == "date":
        return dt.strftime("%Y年%m月%d日")
    elif format_type == "time":
        return dt.strftime("%H時%M分")
    elif format_type == "short":
        return dt.strftime("%m/%d %H:%M")
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: int) -> str:
    """秒数を時間形式にフォーマット"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes}分"
        else:
            return f"{minutes}分{remaining_seconds}秒"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        
        if remaining_seconds == 0 and remaining_minutes == 0:
            return f"{hours}時間"
        elif remaining_seconds == 0:
            return f"{hours}時間{remaining_minutes}分"
        else:
            return f"{hours}時間{remaining_minutes}分{remaining_seconds}秒"


def format_file_size_human(size_bytes: int) -> str:
    """ファイルサイズを人間が読みやすい形式に変換"""
    if size_bytes == 0:
        return "0バイト"
    
    size_names = ["バイト", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    if i == 0:
        return f"{size_bytes:.0f}{size_names[i]}"
    else:
        return f"{size_bytes:.1f}{size_names[i]}"


def format_phone_number(phone: str) -> str:
    """電話番号をフォーマット（日本）"""
    # 数字以外を除去
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 11 and digits.startswith('0'):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10 and digits.startswith('0'):
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    else:
        return phone


def format_postal_code(postal_code: str) -> str:
    """郵便番号をフォーマット（日本）"""
    # 数字以外を除去
    digits = re.sub(r'\D', '', postal_code)
    
    if len(digits) == 7:
        return f"{digits[:3]}-{digits[3:]}"
    else:
        return postal_code


def format_credit_card(card_number: str, mask_char: str = "*") -> str:
    """クレジットカード番号をマスクしてフォーマット"""
    # 数字以外を除去
    digits = re.sub(r'\D', '', card_number)
    
    if len(digits) >= 4:
        masked = mask_char * (len(digits) - 4) + digits[-4:]
        # 4桁ずつ区切る
        chunks = [masked[i:i+4] for i in range(0, len(masked), 4)]
        return " ".join(chunks)
    else:
        return card_number


def format_json_pretty(data: Any, indent: int = 2) -> str:
    """JSONを読みやすくフォーマット"""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(data)


def format_list_to_text(items: List[str], conjunction: str = "と") -> str:
    """リストを日本語の文章形式に変換"""
    if not items:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]}{conjunction}{items[1]}"
    else:
        return f"{', '.join(items[:-1])}{conjunction}{items[-1]}"


def format_plural(count: int, singular: str, plural: str = None) -> str:
    """単数・複数形を適切にフォーマット"""
    if plural is None:
        # 英語の単純な複数形ルール
        if singular.endswith('y') and not singular.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
            plural = singular[:-1] + 'ies'
        elif singular.endswith(('s', 'sh', 'ch', 'x', 'z')):
            plural = singular + 'es'
        else:
            plural = singular + 's'
    
    if count == 1:
        return f"{count} {singular}"
    else:
        return f"{count} {plural}"


def format_relative_time(dt: datetime) -> str:
    """相対的な時間を日本語でフォーマット"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return "昨日"
        elif diff.days < 7:
            return f"{diff.days}日前"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks}週間前"
        else:
            months = diff.days // 30
            return f"{months}ヶ月前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}時間前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分前"
    else:
        return "今"


def format_address(address_parts: Dict[str, str]) -> str:
    """住所を日本語形式でフォーマット"""
    parts = []
    
    # 郵便番号
    if 'postal_code' in address_parts:
        parts.append(format_postal_code(address_parts['postal_code']))
    
    # 都道府県
    if 'prefecture' in address_parts:
        parts.append(address_parts['prefecture'])
    
    # 市区町村
    if 'city' in address_parts:
        parts.append(address_parts['city'])
    
    # 番地・建物名
    if 'street' in address_parts:
        parts.append(address_parts['street'])
    
    if 'building' in address_parts:
        parts.append(address_parts['building'])
    
    return " ".join(parts)


def format_error_message(error: Exception, include_traceback: bool = False) -> str:
    """エラーメッセージをフォーマット"""
    error_type = type(error).__name__
    error_msg = str(error)
    
    if include_traceback:
        import traceback
        tb = traceback.format_exc()
        return f"{error_type}: {error_msg}\n{tb}"
    else:
        return f"{error_type}: {error_msg}"
