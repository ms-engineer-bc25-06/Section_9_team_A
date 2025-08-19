from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CompanySize(str, Enum):
    """企業規模の定義"""
    STARTUP = "startup"      # スタートアップ（従業員50名未満、設立5年未満）
    MEDIUM = "medium"        # 中堅企業（従業員50-1000名、設立5-20年）
    LARGE = "large"          # 大企業（従業員1000名以上、設立20年以上）


class BenchmarkStatus(str, Enum):
    """ベンチマークのステータス"""
    ACTIVE = "active"        # 有効
    INACTIVE = "inactive"    # 無効
    DRAFT = "draft"          # 下書き
    ARCHIVED = "archived"    # アーカイブ


class RequestStatus(str, Enum):
    """リクエストのステータス"""
    PENDING = "pending"      # 承認待ち
    APPROVED = "approved"    # 承認済み
    REJECTED = "rejected"    # 却下
    UNDER_REVIEW = "under_review"  # レビュー中


class IndustryBenchmarkCreate(BaseModel):
    """業界ベンチマーク作成用スキーマ"""
    industry_name: str = Field(..., min_length=1, max_length=100, description="業界名")
    industry_code: str = Field(..., min_length=1, max_length=50, description="業界コード")
    display_name: str = Field(..., min_length=1, max_length=200, description="表示名")
    description: Optional[str] = Field(None, description="業界の説明")
    
    company_size: CompanySize = Field(..., description="企業規模")
    company_size_display: str = Field(..., min_length=1, max_length=100, description="企業規模の表示名")
    
    # メトリクスデータ
    communication_skills_avg: float = Field(0.75, ge=0.0, le=1.0, description="コミュニケーションスキル平均")
    leadership_avg: float = Field(0.75, ge=0.0, le=1.0, description="リーダーシップ平均")
    collaboration_avg: float = Field(0.75, ge=0.0, le=1.0, description="協働性平均")
    problem_solving_avg: float = Field(0.75, ge=0.0, le=1.0, description="問題解決平均")
    emotional_intelligence_avg: float = Field(0.75, ge=0.0, le=1.0, description="感情知性平均")
    
    # ベストプラクティス
    best_practices: List[str] = Field(default_factory=list, description="ベストプラクティス")
    
    # データの信頼性
    data_source: str = Field(..., min_length=1, max_length=200, description="データソース")
    data_source_url: Optional[str] = Field(None, max_length=500, description="データソースURL")
    confidence_level: float = Field(0.8, ge=0.0, le=1.0, description="データの信頼度")
    
    # 管理設定
    is_public: bool = Field(True, description="公開フラグ")
    tags: Optional[List[str]] = Field(default_factory=list, description="タグ")
    notes: Optional[str] = Field(None, description="管理者用メモ")


class IndustryBenchmarkUpdate(BaseModel):
    """業界ベンチマーク更新用スキーマ"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200, description="表示名")
    description: Optional[str] = Field(None, description="業界の説明")
    
    company_size_display: Optional[str] = Field(None, min_length=1, max_length=100, description="企業規模の表示名")
    
    # メトリクスデータ
    communication_skills_avg: Optional[float] = Field(None, ge=0.0, le=1.0, description="コミュニケーションスキル平均")
    leadership_avg: Optional[float] = Field(None, ge=0.0, le=1.0, description="リーダーシップ平均")
    collaboration_avg: Optional[float] = Field(None, ge=0.0, le=1.0, description="協働性平均")
    problem_solving_avg: Optional[float] = Field(None, ge=0.0, le=1.0, description="問題解決平均")
    emotional_intelligence_avg: Optional[float] = Field(None, ge=0.0, le=1.0, description="感情知性平均")
    
    # ベストプラクティス
    best_practices: Optional[List[str]] = Field(None, description="ベストプラクティス")
    
    # データの信頼性
    data_source: Optional[str] = Field(None, min_length=1, max_length=200, description="データソース")
    data_source_url: Optional[str] = Field(None, max_length=500, description="データソースURL")
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="データの信頼度")
    
    # 管理設定
    is_public: Optional[bool] = Field(None, description="公開フラグ")
    is_active: Optional[bool] = Field(None, description="有効フラグ")
    tags: Optional[List[str]] = Field(None, description="タグ")
    notes: Optional[str] = Field(None, description="管理者用メモ")


class IndustryBenchmarkResponse(BaseModel):
    """業界ベンチマーク応答用スキーマ"""
    id: int = Field(..., description="ベンチマークID")
    industry_name: str = Field(..., description="業界名")
    industry_code: str = Field(..., description="業界コード")
    display_name: str = Field(..., description="表示名")
    description: Optional[str] = Field(None, description="業界の説明")
    
    company_size: CompanySize = Field(..., description="企業規模")
    company_size_display: str = Field(..., description="企業規模の表示名")
    
    # メトリクスデータ
    communication_skills_avg: float = Field(..., description="コミュニケーションスキル平均")
    leadership_avg: float = Field(..., description="リーダーシップ平均")
    collaboration_avg: float = Field(..., description="協働性平均")
    problem_solving_avg: float = Field(..., description="問題解決平均")
    emotional_intelligence_avg: float = Field(..., description="感情知性平均")
    
    # ベストプラクティス
    best_practices: List[str] = Field(..., description="ベストプラクティス")
    
    # データの信頼性
    data_source: str = Field(..., description="データソース")
    data_source_url: Optional[str] = Field(None, description="データソースURL")
    last_updated: datetime = Field(..., description="最終更新日時")
    confidence_level: float = Field(..., description="データの信頼度")
    
    # 管理設定
    is_active: bool = Field(..., description="有効フラグ")
    is_public: bool = Field(..., description="公開フラグ")
    created_by: Optional[int] = Field(None, description="作成者ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    
    # メタデータ
    tags: List[str] = Field(..., description="タグ")
    notes: Optional[str] = Field(None, description="管理者用メモ")
    
    class Config:
        from_attributes = True


class IndustryBenchmarkRequestCreate(BaseModel):
    """業界ベンチマーク追加リクエスト作成用スキーマ"""
    industry_name: str = Field(..., min_length=1, max_length=100, description="業界名")
    industry_code: str = Field(..., min_length=1, max_length=50, description="業界コード")
    company_size: CompanySize = Field(..., description="企業規模")
    
    # データ内容
    proposed_metrics: Dict[str, float] = Field(..., description="提案されたメトリクス")
    proposed_best_practices: List[str] = Field(..., description="提案されたベストプラクティス")
    data_source: str = Field(..., min_length=1, max_length=200, description="データソース")
    
    # 追加情報
    description: Optional[str] = Field(None, description="業界の説明")
    justification: Optional[str] = Field(None, description="追加の理由・根拠")


class IndustryBenchmarkRequestUpdate(BaseModel):
    """業界ベンチマーク追加リクエスト更新用スキーマ"""
    status: RequestStatus = Field(..., description="ステータス")
    review_notes: Optional[str] = Field(None, description="レビューコメント")


class IndustryBenchmarkRequestResponse(BaseModel):
    """業界ベンチマーク追加リクエスト応答用スキーマ"""
    id: int = Field(..., description="リクエストID")
    requester_id: int = Field(..., description="リクエスト者ID")
    requester_role: Optional[str] = Field(None, description="リクエスト者の役割")
    
    # 業界情報
    industry_name: str = Field(..., description="業界名")
    industry_code: str = Field(..., description="業界コード")
    company_size: CompanySize = Field(..., description="企業規模")
    
    # データ内容
    proposed_metrics: Dict[str, float] = Field(..., description="提案されたメトリクス")
    proposed_best_practices: List[str] = Field(..., description="提案されたベストプラクティス")
    data_source: str = Field(..., description="データソース")
    
    # リクエスト状況
    status: RequestStatus = Field(..., description="ステータス")
    reviewed_by: Optional[int] = Field(None, description="レビュー担当者ID")
    review_notes: Optional[str] = Field(None, description="レビューコメント")
    reviewed_at: Optional[datetime] = Field(None, description="レビュー日時")
    
    # タイムスタンプ
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    
    class Config:
        from_attributes = True


class IndustryBenchmarkFilter(BaseModel):
    """業界ベンチマークフィルター用スキーマ"""
    industry_name: Optional[str] = Field(None, description="業界名フィルター")
    company_size: Optional[CompanySize] = Field(None, description="企業規模フィルター")
    is_active: Optional[bool] = Field(None, description="有効フラグフィルター")
    is_public: Optional[bool] = Field(None, description="公開フラグフィルター")
    tags: Optional[List[str]] = Field(None, description="タグフィルター")
    created_by: Optional[int] = Field(None, description="作成者フィルター")


class IndustryBenchmarkBulkCreate(BaseModel):
    """業界ベンチマーク一括作成用スキーマ"""
    benchmarks: List[IndustryBenchmarkCreate] = Field(..., description="作成するベンチマークのリスト")
    skip_duplicates: bool = Field(True, description="重複をスキップするか")


class IndustryBenchmarkImport(BaseModel):
    """業界ベンチマークインポート用スキーマ"""
    file_format: str = Field("csv", description="ファイル形式（csv, json, excel）")
    file_content: str = Field(..., description="ファイル内容（Base64エンコード）")
    overwrite_existing: bool = Field(False, description="既存データを上書きするか")
    validation_mode: bool = Field(True, description="バリデーションモード（true: 検証のみ、false: 実際にインポート）")


class IndustryBenchmarkExport(BaseModel):
    """業界ベンチマークエクスポート用スキーマ"""
    file_format: str = Field("csv", description="ファイル形式（csv, json, excel）")
    include_inactive: bool = Field(False, description="無効なデータも含めるか")
    include_metadata: bool = Field(True, description="メタデータも含めるか")
    filters: Optional[IndustryBenchmarkFilter] = Field(None, description="フィルター条件")


class IndustryBenchmarkStats(BaseModel):
    """業界ベンチマーク統計情報用スキーマ"""
    total_benchmarks: int = Field(..., description="総ベンチマーク数")
    active_benchmarks: int = Field(..., description="有効なベンチマーク数")
    public_benchmarks: int = Field(..., description="公開されているベンチマーク数")
    
    # 業界別統計
    industry_counts: Dict[str, int] = Field(..., description="業界別のベンチマーク数")
    company_size_counts: Dict[str, int] = Field(..., description="企業規模別のベンチマーク数")
    
    # データ品質統計
    average_confidence: float = Field(..., description="平均信頼度")
    recently_updated: int = Field(..., description="最近更新されたベンチマーク数（30日以内）")
    
    # 利用統計
    total_requests: int = Field(..., description="総リクエスト数")
    pending_requests: int = Field(..., description="承認待ちリクエスト数")
    approved_requests: int = Field(..., description="承認済みリクエスト数")
