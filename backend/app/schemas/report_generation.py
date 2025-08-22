from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ReportFormat(str, Enum):
    """レポート形式の定義"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"


class ReportType(str, Enum):
    """レポートタイプの定義"""
    COMPARISON = "comparison"
    TEAM = "team"
    INDUSTRY = "industry"
    COMBINED = "combined"


class ChartType(str, Enum):
    """チャートタイプの定義"""
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    RADAR_CHART = "radar_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE_CHART = "gauge_chart"
    FUNNEL_CHART = "funnel_chart"


class VisualizationConfig(BaseModel):
    """可視化設定用スキーマ"""
    chart_type: ChartType = Field(..., description="チャートタイプ")
    title: str = Field(..., description="チャートタイトル")
    description: Optional[str] = Field(None, description="チャートの説明")
    
    # データ設定
    data_source: str = Field(..., description="データソース")
    x_axis: Optional[str] = Field(None, description="X軸の項目")
    y_axis: Optional[str] = Field(None, description="Y軸の項目")
    
    # スタイル設定
    colors: Optional[List[str]] = Field(None, description="チャートカラー")
    theme: Optional[str] = Field("default", description="チャートテーマ")
    animation: Optional[bool] = Field(True, description="アニメーション有効")
    
    # サイズ設定
    width: Optional[int] = Field(800, description="チャート幅（ピクセル）")
    height: Optional[int] = Field(600, description="チャート高さ（ピクセル）")


class ChartData(BaseModel):
    """チャートデータ用スキーマ"""
    chart_id: str = Field(..., description="チャートID")
    chart_type: ChartType = Field(..., description="チャートタイプ")
    title: str = Field(..., description="チャートタイトル")
    
    # データ
    data: Dict[str, Any] = Field(..., description="チャートデータ")
    labels: Optional[List[str]] = Field(None, description="ラベル")
    values: Optional[List[Union[int, float]]] = Field(None, description="値")
    
    # 設定
    config: Optional[VisualizationConfig] = Field(None, description="可視化設定")
    metadata: Optional[Dict[str, Any]] = Field(None, description="メタデータ")


class ReportSection(BaseModel):
    """レポートセクション用スキーマ"""
    section_id: str = Field(..., description="セクションID")
    title: str = Field(..., description="セクションタイトル")
    content: str = Field(..., description="セクション内容")
    
    # セクション設定
    order: int = Field(..., description="表示順序")
    is_visible: bool = Field(True, description="表示フラグ")
    is_collapsible: bool = Field(False, description="折りたたみ可能フラグ")
    
    # コンテンツ
    subsections: Optional[List["ReportSection"]] = Field(None, description="サブセクション")
    charts: Optional[List[ChartData]] = Field(None, description="セクション内のチャート")
    tables: Optional[List[Dict[str, Any]]] = Field(None, description="セクション内のテーブル")


class ReportTemplateConfig(BaseModel):
    """レポートテンプレート設定用スキーマ"""
    template_name: str = Field(..., description="テンプレート名")
    template_code: str = Field(..., description="テンプレートコード")
    
    # レイアウト設定
    sections: List[ReportSection] = Field(..., description="セクション設定")
    default_charts: List[ChartType] = Field(default_factory=list, description="デフォルトチャート")
    
    # スタイル設定
    theme: str = Field("default", description="テーマ")
    color_scheme: List[str] = Field(default_factory=list, description="カラースキーム")
    font_family: str = Field("Arial", description="フォントファミリー")
    font_size: int = Field(12, description="フォントサイズ")
    
    # 出力設定
    default_format: ReportFormat = Field(ReportFormat.PDF, description="デフォルト形式")
    page_size: str = Field("A4", description="ページサイズ")
    orientation: str = Field("portrait", description="ページ向き")


class ReportGenerationOptions(BaseModel):
    """レポート生成オプション用スキーマ"""
    # 基本設定
    report_format: ReportFormat = Field(ReportFormat.PDF, description="レポート形式")
    language: str = Field("ja", description="レポート言語")
    template: Optional[str] = Field(None, description="使用テンプレート")
    
    # 内容設定
    include_charts: bool = Field(True, description="チャートを含めるか")
    include_recommendations: bool = Field(True, description="推奨事項を含めるか")
    include_executive_summary: bool = Field(True, description="エグゼクティブサマリーを含めるか")
    include_appendix: bool = Field(False, description="付録を含めるか")
    
    # カスタムセクション
    custom_sections: List[str] = Field(default_factory=list, description="カスタムセクション")
    exclude_sections: List[str] = Field(default_factory=list, description="除外セクション")
    
    # 可視化設定
    chart_theme: Optional[str] = Field(None, description="チャートテーマ")
    chart_colors: Optional[List[str]] = Field(None, description="チャートカラー")
    chart_animation: bool = Field(True, description="チャートアニメーション")
    
    # 出力設定
    quality: str = Field("high", description="出力品質（low, medium, high）")
    compression: bool = Field(True, description="圧縮有効")
    watermark: Optional[str] = Field(None, description="ウォーターマーク")


class ReportExportRequest(BaseModel):
    """レポートエクスポートリクエスト用スキーマ"""
    report_id: str = Field(..., description="レポートID")
    export_format: ReportFormat = Field(..., description="エクスポート形式")
    
    # エクスポート設定
    export_type: str = Field("download", description="エクスポートタイプ（download, email, share）")
    file_name: Optional[str] = Field(None, description="ファイル名")
    
    # 通知設定
    notify_on_completion: bool = Field(False, description="完了時の通知")
    email_address: Optional[str] = Field(None, description="通知先メールアドレス")
    
    # 共有設定
    share_settings: Optional[Dict[str, Any]] = Field(None, description="共有設定")


class ReportShareRequest(BaseModel):
    """レポート共有リクエスト用スキーマ"""
    report_id: str = Field(..., description="レポートID")
    
    # 共有設定
    share_type: str = Field(..., description="共有タイプ（user, team, public, link）")
    permission_level: str = Field("view", description="権限レベル（view, comment, edit）")
    
    # 共有先
    shared_with_users: Optional[List[int]] = Field(None, description="共有先ユーザーID")
    shared_with_teams: Optional[List[int]] = Field(None, description="共有先チームID")
    
    # 共有設定
    expires_at: Optional[datetime] = Field(None, description="有効期限")
    password_protected: bool = Field(False, description="パスワード保護")
    password: Optional[str] = Field(None, description="パスワード")
    
    # 通知設定
    notify_recipients: bool = Field(True, description="共有先への通知")
    custom_message: Optional[str] = Field(None, description="カスタムメッセージ")


class ReportResponse(BaseModel):
    """レポート応答用スキーマ"""
    report_id: str = Field(..., description="レポートID")
    comparison_id: str = Field(..., description="比較分析ID")
    report_type: ReportType = Field(..., description="レポートタイプ")
    
    # レポートの内容
    title: str = Field(..., description="レポートタイトル")
    summary: str = Field(..., description="レポート概要")
    key_findings: List[str] = Field(..., description="主要な発見")
    detailed_analysis: Dict[str, Any] = Field(..., description="詳細分析結果")
    
    # 可視化データ
    visualizations: List[Dict[str, Any]] = Field(..., description="可視化データ")
    charts_data: List[ChartData] = Field(..., description="チャートデータ")
    
    # アクションプラン
    action_items: List[str] = Field(..., description="アクション項目")
    next_steps: List[str] = Field(..., description="次のステップ")
    
    # レポート設定
    report_format: ReportFormat = Field(..., description="レポート形式")
    language: str = Field(..., description="レポート言語")
    
    # 生成情報
    generated_by: int = Field(..., description="生成者ID")
    generated_at: datetime = Field(..., description="生成日時")
    
    # 管理設定
    is_public: bool = Field(..., description="公開フラグ")
    tags: List[str] = Field(..., description="タグ")
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """レポート一覧応答用スキーマ"""
    reports: List[ReportResponse] = Field(..., description="レポート一覧")
    total_count: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    page_size: int = Field(..., description="ページサイズ")
    total_pages: int = Field(..., description="総ページ数")


class ReportFilter(BaseModel):
    """レポートフィルター用スキーマ"""
    report_type: Optional[ReportType] = Field(None, description="レポートタイプフィルター")
    report_format: Optional[ReportFormat] = Field(None, description="レポート形式フィルター")
    language: Optional[str] = Field(None, description="言語フィルター")
    generated_by: Optional[int] = Field(None, description="生成者フィルター")
    is_public: Optional[bool] = Field(None, description="公開フラグフィルター")
    tags: Optional[List[str]] = Field(None, description="タグフィルター")
    date_from: Optional[datetime] = Field(None, description="生成日時（開始）")
    date_to: Optional[datetime] = Field(None, description="生成日時（終了）")


class ReportStats(BaseModel):
    """レポート統計情報用スキーマ"""
    total_reports: int = Field(..., description="総レポート数")
    reports_by_type: Dict[str, int] = Field(..., description="タイプ別レポート数")
    reports_by_format: Dict[str, int] = Field(..., description="形式別レポート数")
    
    # 生成統計
    reports_generated_today: int = Field(..., description="今日生成されたレポート数")
    reports_generated_this_week: int = Field(..., description="今週生成されたレポート数")
    reports_generated_this_month: int = Field(..., description="今月生成されたレポート数")
    
    # 利用統計
    most_popular_templates: List[str] = Field(..., description="人気テンプレート")
    average_generation_time: float = Field(..., description="平均生成時間（秒）")
    export_success_rate: float = Field(..., description="エクスポート成功率")
