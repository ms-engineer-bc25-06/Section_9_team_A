import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisResult,
    PersonalityTrait, CommunicationPattern, BehaviorScore, AnalysisType
)
from app.integrations.openai_client import OpenAIClient
from app.core.exceptions import AnalysisError

logger = structlog.get_logger()

class AIAnalysisService:
    """AI分析サービス"""
    
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
    async def analyze_text(
        self,
        db: AsyncSession,
        user: User,
        text_content: str,
        analysis_types: List[AnalysisType],
        voice_session_id: Optional[int] = None,
        transcription_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[AnalysisResponse]:
        """テキスト内容を分析"""
        try:
            analyses = []
            
            for analysis_type in analysis_types:
                # 分析実行
                analysis_result = await self._execute_analysis(
                    text_content, analysis_type, user, metadata
                )
                
                # データベースに保存
                analysis = await self._save_analysis(
                    db, user, analysis_type, text_content, analysis_result,
                    voice_session_id, transcription_id
                )
                
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            logger.error("分析実行中にエラーが発生", error=str(e), user_id=user.id)
            raise AnalysisError(f"分析の実行に失敗しました: {str(e)}")
    
    async def _execute_analysis(
        self,
        text_content: str,
        analysis_type: AnalysisType,
        user: User,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """特定の分析タイプを実行"""
        start_time = datetime.now()
        
        try:
            if analysis_type == AnalysisType.PERSONALITY:
                result = await self._analyze_personality(text_content, user, metadata)
            elif analysis_type == AnalysisType.COMMUNICATION:
                result = await self._analyze_communication_patterns(text_content, user, metadata)
            elif analysis_type == AnalysisType.BEHAVIOR:
                result = await self._analyze_behavior_traits(text_content, user, metadata)
            elif analysis_type == AnalysisType.SENTIMENT:
                result = await self._analyze_sentiment(text_content, user, metadata)
            elif analysis_type == AnalysisType.TOPIC:
                result = await self._analyze_topics(text_content, user, metadata)
            elif analysis_type == AnalysisType.SUMMARY:
                result = await self._analyze_summary(text_content, user, metadata)
            else:
                raise ValueError(f"未対応の分析タイプ: {analysis_type}")
            
            # 処理時間を計算
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"{analysis_type}分析でエラー", error=str(e))
            raise AnalysisError(f"{analysis_type}分析の実行に失敗しました: {str(e)}")
    
    async def _analyze_personality(
        self, text_content: str, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """個性分析を実行"""
        prompt = f"""
以下のテキストから話者の個性・性格・思考パターンを分析してください。
テキスト: {text_content}

以下の形式でJSONレスポンスを返してください：
{{
    "title": "個性分析結果",
    "summary": "全体的な個性の概要",
    "keywords": ["キーワード1", "キーワード2"],
    "topics": ["話題1", "話題2"],
    "personality_traits": [
        {{
            "trait_name": "特性名",
            "score": 0.8,
            "confidence": 0.9,
            "description": "特性の詳細説明"
        }}
    ],
    "word_count": 単語数,
    "sentence_count": 文数
}}
"""
        
        response = await self.openai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        try:
            result_data = json.loads(response)
            return AnalysisResult(
                analysis_type=AnalysisType.PERSONALITY,
                title=result_data.get("title", "個性分析結果"),
                summary=result_data.get("summary", ""),
                keywords=result_data.get("keywords", []),
                topics=result_data.get("topics", []),
                personality_traits=[
                    PersonalityTrait(**trait) for trait in result_data.get("personality_traits", [])
                ],
                word_count=result_data.get("word_count"),
                sentence_count=result_data.get("sentence_count"),
                confidence_score=0.8  # デフォルト値
            )
        except Exception as e:
            logger.error("個性分析結果のパースに失敗", error=str(e))
            raise AnalysisError("個性分析結果の処理に失敗しました")
    
    async def _analyze_communication_patterns(
        self, text_content: str, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """コミュニケーションパターン分析を実行"""
        prompt = f"""
以下のテキストから話者のコミュニケーションパターンを分析してください。
テキスト: {text_content}

以下の形式でJSONレスポンスを返してください：
{{
    "title": "コミュニケーションパターン分析",
    "summary": "コミュニケーションスタイルの概要",
    "keywords": ["キーワード1", "キーワード2"],
    "topics": ["話題1", "話題2"],
    "communication_patterns": [
        {{
            "pattern_type": "パターンタイプ",
            "frequency": 0.7,
            "effectiveness": 0.8,
            "examples": ["具体例1", "具体例2"]
        }}
    ],
    "word_count": 単語数,
    "sentence_count": 文数
}}
"""
        
        response = await self.openai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        try:
            result_data = json.loads(response)
            return AnalysisResult(
                analysis_type=AnalysisType.COMMUNICATION,
                title=result_data.get("title", "コミュニケーションパターン分析"),
                summary=result_data.get("summary", ""),
                keywords=result_data.get("keywords", []),
                topics=result_data.get("topics", []),
                communication_patterns=[
                    CommunicationPattern(**pattern) for pattern in result_data.get("communication_patterns", [])
                ],
                word_count=result_data.get("word_count"),
                sentence_count=result_data.get("sentence_count"),
                confidence_score=0.8
            )
        except Exception as e:
            logger.error("コミュニケーションパターン分析結果のパースに失敗", error=str(e))
            raise AnalysisError("コミュニケーションパターン分析結果の処理に失敗しました")
    
    async def _analyze_behavior_traits(
        self, text_content: str, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """行動特性分析を実行"""
        prompt = f"""
以下のテキストから話者の行動特性・スキル・能力を分析してください。
テキスト: {text_content}

以下の形式でJSONレスポンスを返してください：
{{
    "title": "行動特性分析",
    "summary": "行動特性の概要",
    "keywords": ["キーワード1", "キーワード2"],
    "topics": ["話題1", "話題2"],
    "behavior_scores": [
        {{
            "category": "カテゴリ名",
            "score": 75.0,
            "level": "中",
            "improvement_suggestions": ["改善提案1", "改善提案2"]
        }}
    ],
    "word_count": 単語数,
    "sentence_count": 文数
}}
"""
        
        response = await self.openai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        try:
            result_data = json.loads(response)
            return AnalysisResult(
                analysis_type=AnalysisType.BEHAVIOR,
                title=result_data.get("title", "行動特性分析"),
                summary=result_data.get("summary", ""),
                keywords=result_data.get("keywords", []),
                topics=result_data.get("topics", []),
                behavior_scores=[
                    BehaviorScore(**score) for score in result_data.get("behavior_scores", [])
                ],
                word_count=result_data.get("word_count"),
                sentence_count=result_data.get("sentence_count"),
                confidence_score=0.8
            )
        except Exception as e:
            logger.error("行動特性分析結果のパースに失敗", error=str(e))
            raise AnalysisError("行動特性分析結果の処理に失敗しました")
    
    async def _analyze_sentiment(
        self, text_content: str, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """感情分析を実行"""
        prompt = f"""
以下のテキストの感情を分析してください。
テキスト: {text_content}

以下の形式でJSONレスポンスを返してください：
{{
    "title": "感情分析",
    "summary": "感情の概要",
    "keywords": ["キーワード1", "キーワード2"],
    "topics": ["話題1", "話題2"],
    "sentiment_score": -0.2,
    "sentiment_label": "neutral",
    "word_count": 単語数,
    "sentence_count": 文数
}}
"""
        
        response = await self.openai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.1
        )
        
        try:
            result_data = json.loads(response)
            return AnalysisResult(
                analysis_type=AnalysisType.SENTIMENT,
                title=result_data.get("title", "感情分析"),
                summary=result_data.get("summary", ""),
                keywords=result_data.get("keywords", []),
                topics=result_data.get("topics", []),
                sentiment_score=result_data.get("sentiment_score"),
                sentiment_label=result_data.get("sentiment_label"),
                word_count=result_data.get("word_count"),
                sentence_count=result_data.get("sentence_count"),
                confidence_score=0.9
            )
        except Exception as e:
            logger.error("感情分析結果のパースに失敗", error=str(e))
            raise AnalysisError("感情分析結果の処理に失敗しました")
    
    async def _analyze_topics(
        self, text_content: str, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """トピック分析を実行"""
        prompt = f"""
以下のテキストのトピックを分析してください。
テキスト: {text_content}

以下の形式でJSONレスポンスを返してください：
{{
    "title": "トピック分析",
    "summary": "トピックの概要",
    "keywords": ["キーワード1", "キーワード2"],
    "topics": ["話題1", "話題2"],
    "word_count": 単語数,
    "sentence_count": 文数
}}
"""
        
        response = await self.openai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        try:
            result_data = json.loads(response)
            return AnalysisResult(
                analysis_type=AnalysisType.TOPIC,
                title=result_data.get("title", "トピック分析"),
                summary=result_data.get("summary", ""),
                keywords=result_data.get("keywords", []),
                topics=result_data.get("topics", []),
                word_count=result_data.get("word_count"),
                sentence_count=result_data.get("sentence_count"),
                confidence_score=0.8
            )
        except Exception as e:
            logger.error("トピック分析結果のパースに失敗", error=str(e))
            raise AnalysisError("トピック分析結果の処理に失敗しました")
    
    async def _analyze_summary(
        self, text_content: str, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """要約分析を実行"""
        prompt = f"""
以下のテキストを要約してください。
テキスト: {text_content}

以下の形式でJSONレスポンスを返してください：
{{
    "title": "要約分析",
    "summary": "テキストの要約",
    "keywords": ["キーワード1", "キーワード2"],
    "topics": ["話題1", "話題2"],
    "word_count": 単語数,
    "sentence_count": 文数
}}
"""
        
        response = await self.openai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        try:
            result_data = json.loads(response)
            return AnalysisResult(
                analysis_type=AnalysisType.SUMMARY,
                title=result_data.get("title", "要約分析"),
                summary=result_data.get("summary", ""),
                keywords=result_data.get("keywords", []),
                topics=result_data.get("topics", []),
                word_count=result_data.get("word_count"),
                sentence_count=result_data.get("sentence_count"),
                confidence_score=0.8
            )
        except Exception as e:
            logger.error("要約分析結果のパースに失敗", error=str(e))
            raise AnalysisError("要約分析結果の処理に失敗しました")
    
    async def _save_analysis(
        self,
        db: AsyncSession,
        user: User,
        analysis_type: AnalysisType,
        content: str,
        result: AnalysisResult,
        voice_session_id: Optional[int] = None,
        transcription_id: Optional[int] = None
    ) -> AnalysisResponse:
        """分析結果をデータベースに保存"""
        try:
            # 分析IDを生成
            analysis_id = str(uuid.uuid4())
            
            # 分析モデルを作成
            analysis = Analysis(
                analysis_id=analysis_id,
                analysis_type=analysis_type.value,
                title=result.title,
                content=content,
                summary=result.summary,
                keywords=result.keywords,
                topics=result.topics,
                sentiment_score=result.sentiment_score,
                sentiment_label=result.sentiment_label,
                word_count=result.word_count,
                sentence_count=result.sentence_count,
                speaking_time=result.speaking_time,
                status="completed",
                confidence_score=result.confidence_score,
                voice_session_id=voice_session_id,
                transcription_id=transcription_id,
                user_id=user.id,
                processed_at=datetime.now()
            )
            
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            
            # レスポンス形式に変換
            return AnalysisResponse(
                id=analysis.id,
                analysis_id=analysis.analysis_id,
                analysis_type=analysis_type,
                title=analysis.title,
                content=analysis.content,
                summary=analysis.summary,
                keywords=analysis.keywords,
                topics=analysis.topics,
                result=result,
                sentiment_score=analysis.sentiment_score,
                sentiment_label=analysis.sentiment_label,
                word_count=analysis.word_count,
                sentence_count=analysis.sentence_count,
                speaking_time=analysis.speaking_time,
                status=analysis.status,
                confidence_score=analysis.confidence_score,
                voice_session_id=analysis.voice_session_id,
                transcription_id=analysis.transcription_id,
                user_id=analysis.user_id,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at,
                processed_at=analysis.processed_at
            )
            
        except Exception as e:
            await db.rollback()
            logger.error("分析結果の保存に失敗", error=str(e))
            raise AnalysisError("分析結果の保存に失敗しました")
    
    async def get_user_analyses(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
        analysis_type: Optional[AnalysisType] = None
    ) -> Dict[str, Any]:
        """ユーザーの分析結果一覧を取得"""
        try:
            query = select(Analysis).where(Analysis.user_id == user.id)
            
            if analysis_type:
                query = query.where(Analysis.analysis_type == analysis_type.value)
            
            # 総件数を取得
            count_query = select(Analysis.id).where(Analysis.user_id == user.id)
            if analysis_type:
                count_query = count_query.where(Analysis.analysis_type == analysis_type.value)
            
            total_count = await db.scalar(count_query)
            
            # ページネーション
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(Analysis.created_at.desc())
            
            result = await db.execute(query)
            analyses = result.scalars().all()
            
            # レスポンス形式に変換
            analysis_responses = []
            for analysis in analyses:
                # 簡易的なレスポンス（詳細なresultは含まない）
                response = AnalysisResponse(
                    id=analysis.id,
                    analysis_id=analysis.analysis_id,
                    analysis_type=AnalysisType(analysis.analysis_type),
                    title=analysis.title,
                    content=analysis.content,
                    summary=analysis.summary,
                    keywords=analysis.keywords,
                    topics=analysis.topics,
                    result=None,  # 詳細は別途取得
                    sentiment_score=analysis.sentiment_score,
                    sentiment_label=analysis.sentiment_label,
                    word_count=analysis.word_count,
                    sentence_count=analysis.sentence_count,
                    speaking_time=analysis.speaking_time,
                    status=analysis.status,
                    confidence_score=analysis.confidence_score,
                    voice_session_id=analysis.voice_session_id,
                    transcription_id=analysis.transcription_id,
                    user_id=analysis.user_id,
                    created_at=analysis.created_at,
                    updated_at=analysis.updated_at,
                    processed_at=analysis.processed_at
                )
                analysis_responses.append(response)
            
            return {
                "analyses": analysis_responses,
                "total_count": total_count,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error("分析結果一覧の取得に失敗", error=str(e))
            raise AnalysisError("分析結果一覧の取得に失敗しました")
    
    async def get_analysis_by_id(
        self, db: AsyncSession, analysis_id: str, user: User
    ) -> Optional[AnalysisResponse]:
        """分析IDで分析結果を取得"""
        try:
            query = select(Analysis).where(
                and_(
                    Analysis.analysis_id == analysis_id,
                    Analysis.user_id == user.id
                )
            )
            
            result = await db.execute(query)
            analysis = result.scalar_one_or_none()
            
            if not analysis:
                return None
            
            # 詳細なresultは再構築が必要（簡易版）
            return AnalysisResponse(
                id=analysis.id,
                analysis_id=analysis.analysis_id,
                analysis_type=AnalysisType(analysis.analysis_type),
                title=analysis.title,
                content=analysis.content,
                summary=analysis.summary,
                keywords=analysis.keywords,
                topics=analysis.topics,
                result=None,  # 詳細は別途取得
                sentiment_score=analysis.sentiment_score,
                sentiment_label=analysis.sentiment_label,
                word_count=analysis.word_count,
                sentence_count=analysis.sentence_count,
                speaking_time=analysis.speaking_time,
                status=analysis.status,
                confidence_score=analysis.confidence_score,
                voice_session_id=analysis.voice_session_id,
                transcription_id=analysis.transcription_id,
                user_id=analysis.user_id,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at,
                processed_at=analysis.processed_at
            )
            
        except Exception as e:
            logger.error("分析結果の取得に失敗", error=str(e))
            raise AnalysisError("分析結果の取得に失敗しました")
