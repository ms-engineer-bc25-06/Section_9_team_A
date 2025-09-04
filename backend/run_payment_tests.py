#!/usr/bin/env python3
"""
決済システムテスト実行スクリプト

このスクリプトは決済システムのテストを実行し、結果をレポートします。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """
    決済システムのテストを実行
    
    Args:
        test_type (str): 実行するテストの種類 (all, payment, billing, subscription, integration)
        verbose (bool): 詳細出力を有効にする
        coverage (bool): カバレッジレポートを生成する
        parallel (bool): 並列実行を有効にする
    """
    
    # プロジェクトルートに移動
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # pytestコマンドを構築
    cmd = ["python", "-m", "pytest"]
    
    # テストファイルの選択
    test_files = []
    if test_type == "all":
        test_files = [
            "tests/test_payment_system.py",
            "tests/test_billing_system.py", 
            "tests/test_subscription_system.py",
            "tests/test_payment_integration.py"
        ]
    elif test_type == "payment":
        test_files = ["tests/test_payment_system.py"]
    elif test_type == "billing":
        test_files = ["tests/test_billing_system.py"]
    elif test_type == "subscription":
        test_files = ["tests/test_subscription_system.py"]
    elif test_type == "integration":
        test_files = ["tests/test_payment_integration.py"]
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    cmd.extend(test_files)
    
    # オプションの追加
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=app.services",
            "--cov=app.api.v1",
            "--cov=app.models",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing"
        ])
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # その他のオプション
    cmd.extend([
        "--tb=short",  # 短いトレースバック
        "--strict-markers",  # 未定義マーカーでエラー
        "--disable-warnings",  # 警告を無効化
        "-x",  # 最初の失敗で停止
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)
    
    # テスト実行
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ Tests failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print("=" * 60)
        print(f"❌ Error running tests: {e}")
        return False


def run_specific_test(test_name, verbose=False):
    """
    特定のテストを実行
    
    Args:
        test_name (str): 実行するテスト名
        verbose (bool): 詳細出力を有効にする
    """
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    cmd = ["python", "-m", "pytest", f"-k {test_name}"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "--tb=short",
        "--disable-warnings"
    ])
    
    print(f"Running specific test: {test_name}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ Test passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ Test failed with exit code: {e.returncode}")
        return False


def run_lint_check():
    """コードのリントチェックを実行"""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("Running lint checks...")
    print("=" * 60)
    
    # flake8でリントチェック
    try:
        subprocess.run([
            "python", "-m", "flake8", 
            "tests/test_payment_system.py",
            "tests/test_billing_system.py",
            "tests/test_subscription_system.py", 
            "tests/test_payment_integration.py",
            "--max-line-length=120",
            "--ignore=E203,W503"
        ], check=True)
        print("✅ Lint checks passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lint checks failed with exit code: {e.returncode}")
        return False


def generate_test_report():
    """テストレポートを生成"""
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("Generating test report...")
    print("=" * 60)
    
    cmd = [
        "python", "-m", "pytest",
        "tests/test_payment_system.py",
        "tests/test_billing_system.py",
        "tests/test_subscription_system.py",
        "tests/test_payment_integration.py",
        "--html=test_report.html",
        "--self-contained-html",
        "--cov=app.services",
        "--cov=app.api.v1", 
        "--cov=app.models",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "-v"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Test report generated!")
        print("📊 HTML report: test_report.html")
        print("📈 Coverage report: htmlcov/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate test report: {e.returncode}")
        return False


def main():
    """メイン関数"""
    
    parser = argparse.ArgumentParser(description="決済システムテスト実行スクリプト")
    
    parser.add_argument(
        "--type", 
        choices=["all", "payment", "billing", "subscription", "integration"],
        default="all",
        help="実行するテストの種類"
    )
    
    parser.add_argument(
        "--test",
        help="特定のテスト名を実行"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細出力を有効にする"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true", 
        help="カバレッジレポートを生成する"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="並列実行を有効にする"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="リントチェックを実行する"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="テストレポートを生成する"
    )
    
    args = parser.parse_args()
    
    print("🚀 決済システムテスト実行スクリプト")
    print("=" * 60)
    
    success = True
    
    # リントチェック
    if args.lint:
        success &= run_lint_check()
        if not success:
            return 1
    
    # 特定のテスト実行
    if args.test:
        success &= run_specific_test(args.test, args.verbose)
    # テストレポート生成
    elif args.report:
        success &= generate_test_report()
    # 通常のテスト実行
    else:
        success &= run_tests(
            test_type=args.type,
            verbose=args.verbose,
            coverage=args.coverage,
            parallel=args.parallel
        )
    
    print("=" * 60)
    if success:
        print("🎉 全ての処理が正常に完了しました!")
        return 0
    else:
        print("💥 エラーが発生しました。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
