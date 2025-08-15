import pytest
from datetime import datetime, timezone
from app.utils.helpers import (
    format_datetime,
    validate_email,
    generate_random_string,
    sanitize_html,
    truncate_text,
)


class TestFormatDateTime:
    """日時フォーマット関数のテスト"""

    def test_format_datetime_with_timezone(self):
        """タイムゾーン付きの日時フォーマット"""
        dt = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_datetime(dt)
        assert "2024-01-15" in result
        assert "14:30" in result

    def test_format_datetime_without_timezone(self):
        """タイムゾーンなしの日時フォーマット"""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt)
        assert "2024-01-15" in result
        assert "14:30" in result

    def test_format_datetime_none(self):
        """None値の処理"""
        result = format_datetime(None)
        assert result == "N/A"


class TestValidateEmail:
    """メールアドレス検証関数のテスト"""

    def test_valid_email_addresses(self):
        """有効なメールアドレス"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.jp",
            "user+tag@example.org",
            "123@example.com",
        ]
        for email in valid_emails:
            assert validate_email(email) is True

    def test_invalid_email_addresses(self):
        """無効なメールアドレス"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "",
            None,
        ]
        for email in invalid_emails:
            assert validate_email(email) is False


class TestGenerateRandomString:
    """ランダム文字列生成関数のテスト"""

    def test_generate_random_string_default_length(self):
        """デフォルト長でのランダム文字列生成"""
        result = generate_random_string()
        assert len(result) == 8
        assert result.isalnum()

    def test_generate_random_string_custom_length(self):
        """カスタム長でのランダム文字列生成"""
        length = 16
        result = generate_random_string(length)
        assert len(result) == length
        assert result.isalnum()

    def test_generate_random_string_different_results(self):
        """異なる結果が生成されることを確認"""
        result1 = generate_random_string()
        result2 = generate_random_string()
        assert result1 != result2

    def test_generate_random_string_invalid_length(self):
        """無効な長さの処理"""
        with pytest.raises(ValueError):
            generate_random_string(0)
        
        with pytest.raises(ValueError):
            generate_random_string(-1)


class TestSanitizeHtml:
    """HTMLサニタイズ関数のテスト"""

    def test_sanitize_html_safe_tags(self):
        """安全なHTMLタグの処理"""
        html = "<p>Hello <strong>World</strong></p>"
        result = sanitize_html(html)
        assert "<p>" in result
        assert "<strong>" in result
        assert "Hello" in result
        assert "World" in result

    def test_sanitize_html_script_tags(self):
        """スクリプトタグの除去"""
        html = "<p>Hello</p><script>alert('xss')</script>"
        result = sanitize_html(html)
        assert "<p>" in result
        assert "Hello" in result
        assert "<script>" not in result
        assert "alert('xss')" not in result

    def test_sanitize_html_event_handlers(self):
        """イベントハンドラーの除去"""
        html = '<p onclick="alert(\'xss\')">Click me</p>'
        result = sanitize_html(html)
        assert "<p>" in result
        assert "Click me" in result
        assert "onclick" not in result

    def test_sanitize_html_empty_input(self):
        """空の入力の処理"""
        assert sanitize_html("") == ""
        assert sanitize_html(None) == ""

    def test_sanitize_html_complex_html(self):
        """複雑なHTMLの処理"""
        html = """
        <div class="container">
            <h1>Title</h1>
            <p>Content with <a href="https://example.com">link</a></p>
            <script>malicious()</script>
            <iframe src="javascript:alert('xss')"></iframe>
        </div>
        """
        result = sanitize_html(html)
        assert "<div>" in result
        assert "<h1>" in result
        assert "<p>" in result
        assert "<a href=" in result
        assert "Title" in result
        assert "Content with" in result
        assert "link" in result
        assert "<script>" not in result
        assert "<iframe>" not in result


class TestTruncateText:
    """テキスト切り詰め関数のテスト"""

    def test_truncate_text_short(self):
        """短いテキストの処理"""
        text = "Hello World"
        result = truncate_text(text, 20)
        assert result == "Hello World"

    def test_truncate_text_long(self):
        """長いテキストの切り詰め"""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, 20)
        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

    def test_truncate_text_exact_length(self):
        """正確な長さでの切り詰め"""
        text = "Exactly twenty chars"
        result = truncate_text(text, 20)
        assert result == "Exactly twenty chars"

    def test_truncate_text_empty_input(self):
        """空の入力の処理"""
        assert truncate_text("", 10) == ""
        assert truncate_text(None, 10) == ""

    def test_truncate_text_invalid_length(self):
        """無効な長さの処理"""
        with pytest.raises(ValueError):
            truncate_text("Hello", 0)
        
        with pytest.raises(ValueError):
            truncate_text("Hello", -1)

    def test_truncate_text_custom_suffix(self):
        """カスタムサフィックスの使用"""
        text = "Very long text that needs truncation"
        result = truncate_text(text, 15, suffix="***")
        assert len(result) <= 18  # 15 + "***"
        assert result.endswith("***")
