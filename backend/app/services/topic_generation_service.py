from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime

from app.schemas.topic_generation import (
    TopicGenerationRequest,
    TopicGenerationResult,
    TopicSuggestion,
    TopicCategory,
    TopicDifficulty,
    PersonalizedTopicRequest
)
from app.schemas.analysis import AnalysisResult
from app.core.exceptions import AnalysisError
from app.integrations.openai_client import OpenAIClient
from app.repositories import analysis_repository, user_repository


class TopicGenerationService:
    """トークテーマ生成サービス"""
    
    def __init__(
        self,
        openai_client: OpenAIClient,
        analysis_repository=analysis_repository,
        user_repository=user_repository
    ):
        self.openai_client = openai_client
        self.analysis_repository = analysis_repository
        self.user_repository = user_repository
    
    async def generate_topics(
        self, 
        request: TopicGenerationRequest
    ) -> TopicGenerationResult:
        """会話内容に基づいてトークテーマを生成"""
        try:
            # 1. 既存の分析結果を取得
            existing_analyses = await self._get_existing_analyses(
                request.user_id, 
                request.analysis_types
            )
            
            # 2. 参加者の興味・関心を分析
            participant_interests = await self._analyze_participant_interests(
                request.participant_ids
            )
            
            # 3. AIを使用してトークテーマを生成
            generated_topics = await self._generate_topics_with_ai(
                request.text_content,
                existing_analyses,
                participant_interests,
                request.preferred_categories,
                request.max_duration,
                request.difficulty_level
            )
            
            # 4. 結果を構築
            result = TopicGenerationResult(
                generation_id=str(uuid.uuid4()),
                user_id=request.user_id,
                participant_ids=request.participant_ids,
                generated_at=datetime.utcnow(),
                topics=generated_topics,
                generation_reason=self._generate_reason(existing_analyses, participant_interests),
                analysis_summary=self._create_analysis_summary(existing_analyses),
                total_score=self._calculate_total_score(generated_topics)
            )
            
            return result
            
        except Exception as e:
            raise AnalysisError(f"トークテーマ生成に失敗しました: {str(e)}")
    
    async def generate_personalized_topics(
        self, 
        request: PersonalizedTopicRequest
    ) -> TopicGenerationResult:
        """参加者の興味・関心に基づいて個別化されたトークテーマを生成"""
        try:
            # 1. 参加者の分析結果を取得
            participant_analyses = await self._get_participant_analyses(
                request.participant_ids,
                request.analysis_types
            )
            
            # 2. 個別化されたトピックを生成
            personalized_topics = await self._generate_personalized_topics_with_ai(
                participant_analyses,
                request.preferred_categories,
                request.max_duration,
                request.difficulty_level
            )
            
            # 3. 結果を構築
            result = TopicGenerationResult(
                generation_id=str(uuid.uuid4()),
                user_id=request.user_id,
                participant_ids=request.participant_ids,
                generated_at=datetime.utcnow(),
                topics=personalized_topics,
                generation_reason="参加者の興味・関心に基づく個別化されたテーマ提案",
                analysis_summary=self._create_participant_summary(participant_analyses),
                total_score=self._calculate_total_score(personalized_topics)
            )
            
            return result
            
        except Exception as e:
            raise AnalysisError(f"個別化トークテーマ生成に失敗しました: {str(e)}")
    
    async def _get_existing_analyses(
        self, 
        user_id: int, 
        analysis_types: List[str]
    ) -> List[AnalysisResult]:
        """既存の分析結果を取得"""
        analyses = []
        for analysis_type in analysis_types:
            user_analyses = await self.analysis_repository.get_user_analyses(
                user_id=user_id,
                analysis_type=analysis_type,
                limit=10
            )
            analyses.extend(user_analyses)
        return analyses
    
    async def _get_participant_analyses(
        self, 
        participant_ids: List[int], 
        analysis_types: List[str]
    ) -> Dict[int, List[AnalysisResult]]:
        """参加者の分析結果を取得"""
        participant_analyses = {}
        for participant_id in participant_ids:
            analyses = []
            for analysis_type in analysis_types:
                user_analyses = await self.analysis_repository.get_user_analyses(
                    user_id=participant_id,
                    analysis_type=analysis_type,
                    limit=5
                )
                analyses.extend(user_analyses)
            participant_analyses[participant_id] = analyses
        return participant_analyses
    
    async def _analyze_participant_interests(
        self, 
        participant_ids: List[int]
    ) -> Dict[str, Any]:
        """参加者の興味・関心を分析"""
        interests = {}
        for participant_id in participant_ids:
            user = await self.user_repository.get_user_by_id(participant_id)
            if user:
                # ユーザーの基本情報から興味・関心を推定
                interests[participant_id] = {
                    "department": user.department,
                    "hobbies": getattr(user, 'hobbies', ''),
                    "interests": getattr(user, 'interests', ''),
                    "background": getattr(user, 'background', '')
                }
        return interests
    
    async def _generate_topics_with_ai(
        self,
        text_content: str,
        existing_analyses: List[AnalysisResult],
        participant_interests: Dict[str, Any],
        preferred_categories: Optional[List[TopicCategory]],
        max_duration: Optional[int],
        difficulty_level: Optional[TopicDifficulty]
    ) -> List[TopicSuggestion]:
        """AIを使用してトークテーマを生成"""
        
        # 分析結果の要約を作成
        analysis_summary = self._create_analysis_summary(existing_analyses)
        
        # 参加者の興味・関心の要約を作成
        interests_summary = self._create_interests_summary(participant_interests)
        
        # カテゴリと難易度の制約を作成
        constraints = self._create_constraints(
            preferred_categories, max_duration, difficulty_level
        )
        
        # AIプロンプトを作成
        prompt = self._create_topic_generation_prompt(
            text_content, analysis_summary, interests_summary, constraints
        )
        
        try:
            # OpenAI APIを呼び出し
            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4",
                temperature=0.7,
                max_tokens=2000
            )
            
            # レスポンスをパース
            topics_data = json.loads(response.choices[0].message.content)
            return [TopicSuggestion(**topic) for topic in topics_data["topics"]]
            
        except Exception as e:
            # フォールバック: 基本的なテーマを生成
            return self._generate_fallback_topics(
                preferred_categories, max_duration, difficulty_level
            )
    
    async def _generate_personalized_topics_with_ai(
        self,
        participant_analyses: Dict[int, List[AnalysisResult]],
        preferred_categories: Optional[List[TopicCategory]],
        max_duration: Optional[int],
        difficulty_level: Optional[TopicDifficulty]
    ) -> List[TopicSuggestion]:
        """個別化されたトピックをAIで生成"""
        
        # 参加者の分析結果を統合
        combined_analysis = self._combine_participant_analyses(participant_analyses)
        
        # 制約を作成
        constraints = self._create_constraints(
            preferred_categories, max_duration, difficulty_level
        )
        
        # AIプロンプトを作成
        prompt = self._create_personalized_prompt(combined_analysis, constraints)
        
        try:
            # OpenAI APIを呼び出し
            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4",
                temperature=0.7,
                max_tokens=2000
            )
            
            # レスポンスをパース
            topics_data = json.loads(response.choices[0].message.content)
            return [TopicSuggestion(**topic) for topic in topics_data["topics"]]
            
        except Exception as e:
            # フォールバック: 基本的なテーマを生成
            return self._generate_fallback_topics(
                preferred_categories, max_duration, difficulty_level
            )
    
    def _create_topic_generation_prompt(
        self,
        text_content: str,
        analysis_summary: str,
        interests_summary: str,
        constraints: str
    ) -> str:
        """トークテーマ生成用のAIプロンプトを作成"""
        return f"""
以下の情報に基づいて、魅力的なトークテーマを5つ生成してください。

【会話内容】
{text_content[:1000]}

【分析結果の要約】
{analysis_summary}

【参加者の興味・関心】
{interests_summary}

【制約条件】
{constraints}

以下のJSON形式で回答してください：
{{
  "topics": [
    {{
      "title": "テーマのタイトル",
      "description": "テーマの詳細説明",
      "category": "work|personal|hobby|current_events|technology|culture|sports|food|travel|other",
      "difficulty": "easy|medium|hard",
      "estimated_duration": 15,
      "conversation_starters": ["質問1", "質問2", "質問3"],
      "related_keywords": ["キーワード1", "キーワード2", "キーワード3"],
      "confidence_score": 0.85
    }}
  ]
}}

テーマは会話の流れを自然に促進し、参加者が興味を持てる内容にしてください。
"""
    
    def _create_personalized_prompt(
        self,
        combined_analysis: str,
        constraints: str
    ) -> str:
        """個別化されたトピック生成用のAIプロンプトを作成"""
        return f"""
以下の参加者の分析結果に基づいて、個別化されたトークテーマを5つ生成してください。

【参加者の分析結果】
{combined_analysis}

【制約条件】
{constraints}

以下のJSON形式で回答してください：
{{
  "topics": [
    {{
      "title": "テーマのタイトル",
      "description": "テーマの詳細説明",
      "category": "work|personal|hobby|current_events|technology|culture|sports|food|travel|other",
      "difficulty": "easy|medium|hard",
      "estimated_duration": 15,
      "conversation_starters": ["質問1", "質問2", "質問3"],
      "related_keywords": ["キーワード1", "キーワード2", "キーワード3"],
      "confidence_score": 0.85
    }}
  ]
}}

各参加者の興味・関心を考慮し、全員が楽しめるテーマにしてください。
"""
    
    def _create_analysis_summary(self, analyses: List[AnalysisResult]) -> str:
        """分析結果の要約を作成"""
        if not analyses:
            return "分析結果がありません"
        
        summary_parts = []
        for analysis in analyses[:3]:  # 最新3件のみ
            if analysis.analysis_type == "personality":
                summary_parts.append(f"性格分析: {analysis.summary}")
            elif analysis.analysis_type == "communication":
                summary_parts.append(f"コミュニケーションパターン: {analysis.summary}")
            elif analysis.analysis_type == "behavior":
                summary_parts.append(f"行動特性: {analysis.summary}")
        
        return " | ".join(summary_parts) if summary_parts else "分析結果がありません"
    
    def _create_interests_summary(self, interests: Dict[str, Any]) -> str:
        """興味・関心の要約を作成"""
        if not interests:
            return "参加者の興味・関心情報がありません"
        
        summary_parts = []
        for participant_id, interest_data in interests.items():
            parts = []
            if interest_data.get("department"):
                parts.append(f"部署: {interest_data['department']}")
            if interest_data.get("hobbies"):
                parts.append(f"趣味: {interest_data['hobbies']}")
            if interest_data.get("interests"):
                parts.append(f"関心: {interest_data['interests']}")
            
            if parts:
                summary_parts.append(f"参加者{participant_id}: {', '.join(parts)}")
        
        return " | ".join(summary_parts) if summary_parts else "興味・関心情報がありません"
    
    def _create_constraints(
        self,
        preferred_categories: Optional[List[TopicCategory]],
        max_duration: Optional[int],
        difficulty_level: Optional[TopicDifficulty]
    ) -> str:
        """制約条件の文字列を作成"""
        constraints = []
        
        if preferred_categories:
            categories_str = ", ".join([cat.value for cat in preferred_categories])
            constraints.append(f"希望カテゴリ: {categories_str}")
        
        if max_duration:
            constraints.append(f"最大所要時間: {max_duration}分")
        
        if difficulty_level:
            constraints.append(f"難易度: {difficulty_level.value}")
        
        return " | ".join(constraints) if constraints else "制約条件なし"
    
    def _combine_participant_analyses(
        self, 
        participant_analyses: Dict[int, List[AnalysisResult]]
    ) -> str:
        """参加者の分析結果を統合"""
        combined = []
        for participant_id, analyses in participant_analyses.items():
            if analyses:
                analysis_summary = self._create_analysis_summary(analyses)
                combined.append(f"参加者{participant_id}: {analysis_summary}")
        
        return " | ".join(combined) if combined else "参加者の分析結果がありません"
    
    def _generate_reason(
        self, 
        analyses: List[AnalysisResult], 
        interests: Dict[str, Any]
    ) -> str:
        """生成理由を作成"""
        reasons = []
        
        if analyses:
            reasons.append("既存の分析結果に基づく")
        
        if interests:
            reasons.append("参加者の興味・関心を考慮")
        
        if not reasons:
            reasons.append("基本的な会話促進テーマ")
        
        return "、".join(reasons)
    
    def _calculate_total_score(self, topics: List[TopicSuggestion]) -> float:
        """総合スコアを計算"""
        if not topics:
            return 0.0
        
        total_confidence = sum(topic.confidence_score for topic in topics)
        return round(total_confidence / len(topics), 2)
    
    def _generate_fallback_topics(
        self,
        preferred_categories: Optional[List[TopicCategory]],
        max_duration: Optional[int],
        difficulty_level: Optional[TopicDifficulty]
    ) -> List[TopicSuggestion]:
        """フォールバック用の基本的なテーマを生成"""
        fallback_topics = [
            TopicSuggestion(
                title="最近の出来事について",
                description="最近あった楽しかったことや印象に残った出来事を共有しましょう",
                category=TopicCategory.PERSONAL,
                difficulty=TopicDifficulty.EASY,
                estimated_duration=15,
                conversation_starters=["今週あった楽しいことは？", "最近印象に残った出来事は？"],
                related_keywords=["日常", "出来事", "体験"],
                confidence_score=0.8
            ),
            TopicSuggestion(
                title="趣味・特技の話",
                description="それぞれの趣味や特技について話し合いましょう",
                category=TopicCategory.HOBBY,
                difficulty=TopicDifficulty.EASY,
                estimated_duration=20,
                conversation_starters=["最近ハマっていることは？", "得意なことは？"],
                related_keywords=["趣味", "特技", "興味"],
                confidence_score=0.8
            ),
            TopicSuggestion(
                title="仕事の話",
                description="現在の仕事やプロジェクトについて話し合いましょう",
                category=TopicCategory.WORK,
                difficulty=TopicDifficulty.MEDIUM,
                estimated_duration=25,
                conversation_starters=["今取り組んでいる仕事は？", "仕事で困っていることは？"],
                related_keywords=["仕事", "プロジェクト", "課題"],
                confidence_score=0.7
            )
        ]
        
        # 制約に応じてフィルタリング
        if preferred_categories:
            fallback_topics = [
                topic for topic in fallback_topics 
                if topic.category in preferred_categories
            ]
        
        if max_duration:
            fallback_topics = [
                topic for topic in fallback_topics 
                if topic.estimated_duration <= max_duration
            ]
        
        if difficulty_level:
            fallback_topics = [
                topic for topic in fallback_topics 
                if topic.difficulty == difficulty_level
            ]
        
        return fallback_topics[:3]  # 最大3件
