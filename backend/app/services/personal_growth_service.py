import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.personal_growth import (
    ImprovementPlan, ImprovementStep, GrowthGoal, PersonalGrowthProfile,
    DifficultyLevel, PriorityLevel, GoalStatus
)
from app.schemas.analysis import (
    AnalysisType, AnalysisResult
)
from app.integrations.openai_client import OpenAIClient
from app.core.exceptions import AnalysisError

logger = structlog.get_logger()

class PersonalGrowthService:
    """個人成長支援サービス"""
    
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
    async def generate_improvement_plan(
        self,
        db: AsyncSession,
        user: User,
        analysis_results: List[AnalysisResult],
        target_skills: Optional[Dict[str, float]] = None
    ) -> ImprovementPlan:
        """分析結果に基づいて改善計画を生成"""
        try:
            # 現在の能力レベルを分析
            current_skills = await self._analyze_current_skills(analysis_results)
            
            # 目標設定
            if not target_skills:
                target_skills = await self._generate_target_skills(current_skills)
            
            # 改善ステップを生成
            improvement_steps = await self._generate_improvement_steps(
                current_skills, target_skills, analysis_results
            )
            
            # 改善計画を作成
            improvement_plan = ImprovementPlan(
                id=str(uuid.uuid4()),
                title=f"{user.username}の成長計画",
                description="AI分析に基づく個別化された改善計画",
                current_level=self._get_overall_level(current_skills),
                target_level=self._get_overall_level(target_skills),
                steps=improvement_steps,
                estimated_duration=self._calculate_estimated_duration(improvement_steps),
                priority=self._determine_priority(current_skills, target_skills),
                category="comprehensive",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            logger.info(
                "改善計画生成完了",
                user_id=user.id,
                plan_id=improvement_plan.id,
                steps_count=len(improvement_steps)
            )
            
            return improvement_plan
            
        except Exception as e:
            logger.error("改善計画生成でエラー", error=str(e), user_id=user.id)
            raise AnalysisError(f"改善計画の生成に失敗しました: {str(e)}")
    
    async def _analyze_current_skills(
        self, analysis_results: List[AnalysisResult]
    ) -> Dict[str, float]:
        """分析結果から現在の能力レベルを抽出"""
        skills = {}
        
        for result in analysis_results:
            if result.analysis_type == AnalysisType.PERSONALITY:
                skills.update(self._extract_personality_skills(result))
            elif result.analysis_type == AnalysisType.COMMUNICATION:
                skills.update(self._extract_communication_skills(result))
            elif result.analysis_type == AnalysisType.BEHAVIOR:
                skills.update(self._extract_behavior_skills(result))
        
        return skills
    
    def _extract_personality_skills(self, result: AnalysisResult) -> Dict[str, float]:
        """個性分析からスキルを抽出"""
        skills = {}
        if hasattr(result, 'personality_traits') and result.personality_traits:
            for trait in result.personality_traits:
                skills[f"personality_{trait.trait_name}"] = trait.score / 100.0 * 5.0
        return skills
    
    def _extract_communication_skills(self, result: AnalysisResult) -> Dict[str, float]:
        """コミュニケーション分析からスキルを抽出"""
        skills = {}
        if hasattr(result, 'communication_patterns') and result.communication_patterns:
            for pattern in result.communication_patterns:
                skills[f"communication_{pattern.pattern_name}"] = pattern.score / 100.0 * 5.0
        return skills
    
    def _extract_behavior_skills(self, result: AnalysisResult) -> Dict[str, float]:
        """行動特性分析からスキルを抽出"""
        skills = {}
        if hasattr(result, 'behavior_scores') and result.behavior_scores:
            for behavior in result.behavior_scores:
                skills[f"behavior_{behavior.behavior_name}"] = behavior.score / 100.0 * 5.0
        return skills
    
    async def _generate_target_skills(
        self, current_skills: Dict[str, float]
    ) -> Dict[str, float]:
        """現在のスキルに基づいて目標スキルを生成"""
        target_skills = {}
        
        for skill_name, current_level in current_skills.items():
            # 現在のレベルに応じて適切な目標を設定
            if current_level < 2.0:
                target_skills[skill_name] = min(current_level + 1.5, 5.0)
            elif current_level < 3.5:
                target_skills[skill_name] = min(current_level + 1.0, 5.0)
            else:
                target_skills[skill_name] = min(current_level + 0.5, 5.0)
        
        return target_skills
    
    async def _generate_improvement_steps(
        self,
        current_skills: Dict[str, float],
        target_skills: Dict[str, float],
        analysis_results: List[AnalysisResult]
    ) -> List[ImprovementStep]:
        """改善ステップを生成"""
        steps = []
        step_order = 1
        
        # 優先度の高いスキルから改善ステップを生成
        priority_skills = self._get_priority_skills(current_skills, target_skills)
        
        for skill_name in priority_skills:
            current_level = current_skills.get(skill_name, 0.0)
            target_level = target_skills.get(skill_name, 5.0)
            
            if target_level > current_level:
                step = await self._create_improvement_step(
                    skill_name, current_level, target_level, step_order, analysis_results
                )
                steps.append(step)
                step_order += 1
        
        return steps
    
    def _get_priority_skills(
        self, current_skills: Dict[str, float], target_skills: Dict[str, float]
    ) -> List[str]:
        """優先度の高いスキルを取得"""
        # 改善幅が大きいスキルを優先
        improvement_scores = {}
        for skill_name in current_skills.keys():
            current = current_skills.get(skill_name, 0.0)
            target = target_skills.get(skill_name, 5.0)
            improvement_scores[skill_name] = target - current
        
        # 改善幅でソート
        sorted_skills = sorted(
            improvement_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [skill_name for skill_name, _ in sorted_skills]
    
    async def _create_improvement_step(
        self,
        skill_name: str,
        current_level: float,
        target_level: float,
        order: int,
        analysis_results: List[AnalysisResult]
    ) -> ImprovementStep:
        """個別の改善ステップを作成"""
        # AIを使用して具体的な改善ステップを生成
        prompt = self._create_improvement_prompt(skill_name, current_level, target_level)
        
        try:
            response = await self.openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            # AIの応答を解析してステップを作成
            step_data = self._parse_ai_response(response, skill_name, current_level, target_level)
            
            return ImprovementStep(
                id=str(uuid.uuid4()),
                order=order,
                title=step_data.get("title", f"{skill_name}の改善"),
                description=step_data.get("description", ""),
                action_items=step_data.get("action_items", []),
                resources=step_data.get("resources", []),
                estimated_time=step_data.get("estimated_time", "1-2週間"),
                difficulty=self._determine_difficulty(current_level, target_level),
                dependencies=step_data.get("dependencies", [])
            )
            
        except Exception as e:
            logger.warning(f"AI改善ステップ生成でエラー、フォールバック使用: {str(e)}")
            return self._create_fallback_step(skill_name, current_level, target_level, order)
    
    def _create_improvement_prompt(
        self, skill_name: str, current_level: float, target_level: float
    ) -> str:
        """改善ステップ生成用のプロンプトを作成"""
        return f"""
        スキル名: {skill_name}
        現在のレベル: {current_level}/5.0
        目標レベル: {target_level}/5.0
        
        このスキルを向上させるための具体的な改善ステップを提案してください。
        以下の形式でJSONで回答してください：
        
        {{
            "title": "ステップのタイトル",
            "description": "ステップの詳細説明",
            "action_items": ["具体的なアクション1", "具体的なアクション2"],
            "resources": ["参考リソース1", "参考リソース2"],
            "estimated_time": "推定時間",
            "dependencies": ["依存するスキルや条件"]
        }}
        """
    
    def _parse_ai_response(
        self, response: str, skill_name: str, current_level: float, target_level: float
    ) -> Dict[str, Any]:
        """AIの応答を解析"""
        try:
            # JSONの抽出を試行
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # フォールバック
        return {
            "title": f"{skill_name}の改善",
            "description": f"現在のレベル{current_level}から目標レベル{target_level}への改善",
            "action_items": ["具体的な練習", "フィードバックの収集"],
            "resources": ["オンラインコース", "書籍"],
            "estimated_time": "2-3週間",
            "dependencies": []
        }
    
    def _create_fallback_step(
        self, skill_name: str, current_level: float, target_level: float, order: int
    ) -> ImprovementStep:
        """フォールバック用の改善ステップを作成"""
        return ImprovementStep(
            id=str(uuid.uuid4()),
            order=order,
            title=f"{skill_name}の改善",
            description=f"現在のレベル{current_level}から目標レベル{target_level}への改善を目指します",
            action_items=[
                "定期的な練習",
                "フィードバックの収集",
                "目標設定と進捗管理"
            ],
            resources=["オンライン学習プラットフォーム", "関連書籍", "メンター"],
            estimated_time="2-4週間",
            difficulty=self._determine_difficulty(current_level, target_level),
            dependencies=[]
        )
    
    def _determine_difficulty(self, current_level: float, target_level: float) -> str:
        """難易度を決定"""
        improvement = target_level - current_level
        if improvement <= 0.5:
            return "easy"
        elif improvement <= 1.5:
            return "medium"
        else:
            return "hard"
    
    def _get_overall_level(self, skills: Dict[str, float]) -> str:
        """全体的なレベルを取得"""
        if not skills:
            return "初級"
        
        avg_level = sum(skills.values()) / len(skills)
        if avg_level < 2.0:
            return "初級"
        elif avg_level < 3.5:
            return "中級"
        else:
            return "上級"
    
    def _calculate_estimated_duration(self, steps: List[ImprovementStep]) -> str:
        """推定期間を計算"""
        total_weeks = 0
        for step in steps:
            time_str = step.estimated_time
            if "週間" in time_str:
                try:
                    weeks = int(time_str.split("週間")[0].split("-")[-1])
                    total_weeks += weeks
                except:
                    total_weeks += 2
            else:
                total_weeks += 2
        
        if total_weeks <= 4:
            return f"{total_weeks}週間"
        elif total_weeks <= 12:
            return f"{total_weeks//4}ヶ月"
        else:
            return f"{total_weeks//12}年"
    
    def _determine_priority(
        self, current_skills: Dict[str, float], target_skills: Dict[str, float]
    ) -> str:
        """優先度を決定"""
        total_improvement = sum(
            target_skills.get(skill, 0) - current_skills.get(skill, 0)
            for skill in set(current_skills.keys()) | set(target_skills.keys())
        )
        
        if total_improvement > 5.0:
            return "high"
        elif total_improvement > 2.0:
            return "medium"
        else:
            return "low"
    
    async def create_growth_goal(
        self,
        user: User,
        title: str,
        description: str,
        category: str,
        target_date: Optional[datetime] = None,
        metrics: Optional[List[str]] = None
    ) -> GrowthGoal:
        """成長目標を作成"""
        return GrowthGoal(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            target_date=target_date,
            progress=0.0,
            status="active",
            category=category,
            metrics=metrics or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    async def update_goal_progress(
        self, goal: GrowthGoal, progress: float
    ) -> GrowthGoal:
        """目標の進捗を更新"""
        goal.progress = max(0.0, min(1.0, progress))
        goal.updated_at = datetime.utcnow()
        
        if goal.progress >= 1.0:
            goal.status = "completed"
        
        return goal
