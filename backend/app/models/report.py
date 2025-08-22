from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Report(Base):
    """レポート保存用モデル"""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    # 基本情報
    report_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="レポートID（UUID）",
    )
    comparison_id = Column(
        String(100), nullable=False, index=True, comment="比較分析ID"
    )
    report_type = Column(
        String(50),
        nullable=False,
        comment="レポートタイプ（comparison, team, industry）",
    )

    # レポートの内容
    title = Column(String(200), nullable=False, comment="レポートタイトル")
    summary = Column(Text, comment="レポート概要")
    key_findings = Column(JSON, comment="主要な発見（JSON配列）")
    detailed_analysis = Column(JSON, comment="詳細分析結果（JSON）")

    # 可視化データ
    visualizations = Column(JSON, comment="可視化データ（JSON配列）")
    charts_data = Column(JSON, comment="チャート用データ（JSON）")

    # アクションプラン
    action_items = Column(JSON, comment="アクション項目（JSON配列）")
    next_steps = Column(JSON, comment="次のステップ（JSON配列）")

    # レポート設定
    report_format = Column(
        String(20), default="pdf", comment="レポート形式（pdf, html, json）"
    )
    include_charts = Column(Boolean, default=True, comment="チャートを含めるか")
    include_recommendations = Column(
        Boolean, default=True, comment="推奨事項を含めるか"
    )
    language = Column(String(10), default="ja", comment="レポート言語")

    # 生成情報
    generated_by = Column(Integer, ForeignKey("users.id"), comment="生成者ID")
    generated_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="生成日時"
    )

    # 管理設定
    is_public = Column(Boolean, default=False, comment="公開フラグ")
    is_archived = Column(Boolean, default=False, comment="アーカイブフラグ")
    tags = Column(JSON, comment="タグ（JSON配列）")
    notes = Column(Text, comment="管理者用メモ")

    # タイムスタンプ
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="作成日時"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーション
    user = relationship("User", back_populates="reports")
    exports = relationship("ReportExport", back_populates="report")
    shares = relationship("ReportShare", back_populates="report")


class ReportTemplate(Base):
    """レポートテンプレート用モデル"""

    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)

    # 基本情報
    template_name = Column(String(100), nullable=False, comment="テンプレート名")
    template_code = Column(
        String(50), unique=True, nullable=False, comment="テンプレートコード"
    )
    display_name = Column(String(200), nullable=False, comment="表示名")
    description = Column(Text, comment="テンプレートの説明")

    # テンプレート設定
    template_type = Column(
        String(50),
        nullable=False,
        comment="テンプレートタイプ（comparison, team, industry）",
    )
    default_format = Column(String(20), default="pdf", comment="デフォルト形式")
    default_language = Column(String(10), default="ja", comment="デフォルト言語")

    # テンプレート内容
    title_template = Column(String(200), comment="タイトルテンプレート")
    summary_template = Column(Text, comment="概要テンプレート")
    section_templates = Column(JSON, comment="セクションテンプレート（JSON）")

    # 可視化設定
    default_charts = Column(JSON, comment="デフォルトチャート設定（JSON配列）")
    chart_colors = Column(JSON, comment="チャートカラー設定（JSON）")
    chart_styles = Column(JSON, comment="チャートスタイル設定（JSON）")

    # 管理設定
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    is_default = Column(Boolean, default=False, comment="デフォルトテンプレートフラグ")
    created_by = Column(Integer, ForeignKey("users.id"), comment="作成者ID")

    # タイムスタンプ
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="作成日時"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )


class ReportExport(Base):
    """レポートエクスポート履歴用モデル"""

    __tablename__ = "report_exports"

    id = Column(Integer, primary_key=True, index=True)

    # エクスポート情報
    report_id = Column(
        Integer, ForeignKey("reports.id"), nullable=False, comment="レポートID"
    )
    export_format = Column(String(20), nullable=False, comment="エクスポート形式")
    export_type = Column(
        String(50), comment="エクスポートタイプ（download, email, share）"
    )

    # エクスポート設定
    file_size = Column(Integer, comment="ファイルサイズ（バイト）")
    file_path = Column(String(500), comment="ファイルパス")
    download_url = Column(String(500), comment="ダウンロードURL")

    # エクスポート状況
    status = Column(
        String(50),
        default="processing",
        comment="ステータス（processing, completed, failed）",
    )
    error_message = Column(Text, comment="エラーメッセージ")

    # エクスポート情報
    exported_by = Column(
        Integer, ForeignKey("users.id"), comment="エクスポート実行者ID"
    )
    exported_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="エクスポート日時"
    )

    # タイムスタンプ
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="作成日時"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーション
    report = relationship("Report", back_populates="exports")
    user = relationship("User", back_populates="report_exports")


class ReportShare(Base):
    """レポート共有設定用モデル"""

    __tablename__ = "report_shares"

    id = Column(Integer, primary_key=True, index=True)

    # 共有設定
    report_id = Column(
        Integer, ForeignKey("reports.id"), nullable=False, comment="レポートID"
    )
    shared_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="共有者ID"
    )
    shared_with = Column(Integer, ForeignKey("users.id"), comment="共有先ユーザーID")
    shared_with_team = Column(
        Integer, ForeignKey("organizations.id"), comment="共有先組織ID"
    )

    # 共有設定
    share_type = Column(
        String(50), nullable=False, comment="共有タイプ（user, team, public, link）"
    )
    permission_level = Column(
        String(50), default="view", comment="権限レベル（view, comment, edit）"
    )
    expires_at = Column(DateTime(timezone=True), comment="有効期限")

    # 共有情報
    share_link = Column(String(500), comment="共有リンク")
    access_count = Column(Integer, default=0, comment="アクセス回数")
    last_accessed = Column(DateTime(timezone=True), comment="最終アクセス日時")

    # 管理設定
    is_active = Column(Boolean, default=True, comment="有効フラグ")
    notify_on_access = Column(Boolean, default=False, comment="アクセス時の通知")

    # タイムスタンプ
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="作成日時"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーション
    report = relationship("Report", back_populates="shares")
    shared_by_user = relationship(
        "User", foreign_keys=[shared_by], back_populates="shared_reports"
    )
    shared_with_user = relationship(
        "User", foreign_keys=[shared_with], back_populates="received_reports"
    )
    shared_with_team_rel = relationship("Organization", back_populates="shared_reports")
