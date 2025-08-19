from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class IndustryBenchmark(Base):
    """業界ベンチマークデータモデル"""
    __tablename__ = "industry_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    
    # 基本情報
    industry_name = Column(String(100), nullable=False, index=True, comment="業界名")
    industry_code = Column(String(50), nullable=False, unique=True, index=True, comment="業界コード")
    display_name = Column(String(200), nullable=False, comment="表示名")
    description = Column(Text, comment="業界の説明")
    
    # 企業規模別の設定
    company_size = Column(String(50), nullable=False, index=True, comment="企業規模（startup, medium, large）")
    company_size_display = Column(String(100), comment="企業規模の表示名")
    
    # メトリクスデータ
    communication_skills_avg = Column(Float, default=0.75, comment="コミュニケーションスキル平均")
    leadership_avg = Column(Float, default=0.75, comment="リーダーシップ平均")
    collaboration_avg = Column(Float, default=0.75, comment="協働性平均")
    problem_solving_avg = Column(Float, default=0.75, comment="問題解決平均")
    emotional_intelligence_avg = Column(Float, default=0.75, comment="感情知性平均")
    
    # ベストプラクティス
    best_practices = Column(JSON, comment="ベストプラクティス（JSON配列）")
    
    # データの信頼性
    data_source = Column(String(200), comment="データソース")
    data_source_url = Column(String(500), comment="データソースURL")
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), comment="最終更新日時")
    confidence_level = Column(Float, default=0.8, comment="データの信頼度（0.0-1.0）")
    
    # 管理設定
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    is_public = Column(Boolean, default=True, comment="公開フラグ")
    created_by = Column(Integer, comment="作成者ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新日時")
    
    # メタデータ
    tags = Column(JSON, comment="タグ（JSON配列）")
    notes = Column(Text, comment="管理者用メモ")


class IndustryBenchmarkHistory(Base):
    """業界ベンチマークデータの履歴モデル"""
    __tablename__ = "industry_benchmark_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # 元のデータへの参照
    benchmark_id = Column(Integer, nullable=False, index=True, comment="ベンチマークID")
    
    # 変更前のデータ（JSON形式で保存）
    previous_data = Column(JSON, comment="変更前のデータ")
    
    # 変更情報
    change_type = Column(String(50), comment="変更タイプ（create, update, delete）")
    changed_by = Column(Integer, comment="変更者ID")
    change_reason = Column(Text, comment="変更理由")
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), comment="変更日時")


class IndustryBenchmarkRequest(Base):
    """業界ベンチマーク追加リクエストモデル"""
    __tablename__ = "industry_benchmark_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # リクエスト情報
    requester_id = Column(Integer, nullable=False, comment="リクエスト者ID")
    requester_role = Column(String(100), comment="リクエスト者の役割")
    
    # 業界情報
    industry_name = Column(String(100), nullable=False, comment="業界名")
    industry_code = Column(String(50), nullable=False, comment="業界コード")
    company_size = Column(String(50), nullable=False, comment="企業規模")
    
    # データ内容
    proposed_metrics = Column(JSON, comment="提案されたメトリクス")
    proposed_best_practices = Column(JSON, comment="提案されたベストプラクティス")
    data_source = Column(String(200), comment="データソース")
    
    # リクエスト状況
    status = Column(String(50), default="pending", comment="ステータス（pending, approved, rejected）")
    reviewed_by = Column(Integer, comment="レビュー担当者ID")
    review_notes = Column(Text, comment="レビューコメント")
    reviewed_at = Column(DateTime(timezone=True), comment="レビュー日時")
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新日時")
