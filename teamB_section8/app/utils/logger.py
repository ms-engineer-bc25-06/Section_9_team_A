"""
loguruによる構造化ログ設定
"""

from loguru import logger
import sys


def setup_logger() -> None:
    """
    ログ出力の初期設定を行う関数
    """
    logger.remove()
    logger.add(
        sys.stdout,
        format="[{time:YYYY-MM-DD HH:mm:ss}] [{level}] {message}",
        level="INFO",
    )
