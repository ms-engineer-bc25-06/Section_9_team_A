import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import numpy as np
from datetime import datetime, timedelta

from app.models.team_dynamics import (
    TeamInteraction, TeamCompatibility, TeamCohesion, TeamMemberProfile
)
from app.models.voice_session import VoiceSession
from app.models.transcription import Transcription
from app.models.team import Team
from app.models.user import User
from app.models.team_member import TeamMember
from app.schemas.team_dynamics import (
    TeamInteractionAnalysis, TeamCompatibilityAnalysis, TeamCohesionAnalysis
)

logger = logging.getLogger(__name__)

class TeamDynamicsService:
    """チームダイナミクス分析サービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_team_interactions(
        self, 
        team_id: int, 
        session_id: int,
        transcriptions: List[Transcription]
    ) -> TeamInteractionAnalysis:
        """チーム相互作用パターンを分析"""
        try:
            # 既存のデータをクリア
            self.db.query(TeamInteraction).filter(
                TeamInteraction.team_id == team_id,
                TeamInteraction.session_id == session_id
            ).delete()
            
            # 相互作用パターンを分析
            interactions = self._analyze_interaction_patterns(transcriptions, team_id, session_id)
            
            # 結果を保存
            for interaction in interactions:
                self.db.add(interaction)
            self.db.commit()
            
            # 相互作用メトリクスを計算
            metrics = self._calculate_interaction_metrics(team_id, session_id)
            
            return TeamInteractionAnalysis(
                team_id=team_id,
                session_id=session_id,
                total_interactions=len(interactions),
                interaction_matrix=metrics["interaction_matrix"],
                silent_members=metrics["silent_members"],
                communication_efficiency=metrics["communication_efficiency"],
                interaction_types_distribution=metrics["interaction_types_distribution"]
            )
            
        except Exception as e:
            logger.error(f"チーム相互作用分析でエラーが発生: {e}")
            self.db.rollback()
            raise
    
    def _analyze_interaction_patterns(
        self, 
        transcriptions: List[Transcription], 
        team_id: int, 
        session_id: int
    ) -> List[TeamInteraction]:
        """相互作用パターンを分析してTeamInteractionオブジェクトを生成"""
        interactions = []
        
        # 発言を時系列でソート
        sorted_transcriptions = sorted(transcriptions, key=lambda x: x.timestamp)
        
        for i, current in enumerate(sorted_transcriptions):
            if i == 0:
                continue
                
            previous = sorted_transcriptions[i - 1]
            
            # 相互作用の種類を判定
            interaction_type = self._determine_interaction_type(
                previous.timestamp, 
                current.timestamp,
                previous.speaker_id,
                current.speaker_id
            )
            
            # 相互作用の強度を計算
            interaction_strength = self._calculate_interaction_strength(
                previous.timestamp, 
                current.timestamp
            )
            
            # 相互作用オブジェクトを作成
            interaction = TeamInteraction(
                team_id=team_id,
                session_id=session_id,
                speaker_id=previous.speaker_id,
                listener_id=current.speaker_id,
                interaction_type=interaction_type,
                interaction_strength=interaction_strength,
                timestamp=current.timestamp,
                duration=float((current.timestamp - previous.timestamp).total_seconds())
            )
            
            interactions.append(interaction)
        
        return interactions
    
    def _determine_interaction_type(
        self, 
        prev_timestamp, 
        curr_timestamp, 
        prev_speaker_id: int, 
        curr_speaker_id: int
    ) -> str:
        """相互作用の種類を判定"""
        time_gap = (curr_timestamp - prev_timestamp).total_seconds()
        
        # 同じ話者の場合は継続
        if prev_speaker_id == curr_speaker_id:
            return "continuation"
        
        # 時間ギャップに基づいて相互作用タイプを判定
        if time_gap <= 1.0:
            return "interruption"  # 割り込み
        elif time_gap <= 3.0:
            return "response"       # 即座の応答
        elif time_gap <= 5.0:
            return "support"        # サポート
        else:
            return "challenge"      # 挑戦・質問
    
    def _calculate_interaction_strength(
        self, 
        prev_timestamp, 
        curr_timestamp
    ) -> float:
        """相互作用の強度を計算（0.0-1.0）"""
        time_gap = (curr_timestamp - prev_timestamp).total_seconds()
        
        # 時間ギャップが短いほど強度が高い
        if time_gap <= 1.0:
            return 1.0
        elif time_gap <= 3.0:
            return 0.8
        elif time_gap <= 5.0:
            return 0.6
        elif time_gap <= 10.0:
            return 0.4
        else:
            return 0.2
    
    def _calculate_interaction_metrics(
        self, 
        team_id: int, 
        session_id: int
    ) -> Dict:
        """相互作用メトリクスを計算"""
        interactions = self.db.query(TeamInteraction).filter(
            TeamInteraction.team_id == team_id,
            TeamInteraction.session_id == session_id
        ).all()
        
        # チームメンバーを取得
        team_members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()
        member_ids = [member.user_id for member in team_members]
        
        # 相互作用マトリックスを作成
        interaction_matrix = {}
        for member_id in member_ids:
            interaction_matrix[member_id] = {}
            for other_id in member_ids:
                if member_id != other_id:
                    # 特定のメンバー間の相互作用を集計
                    member_interactions = [
                        i for i in interactions 
                        if i.speaker_id == member_id and i.listener_id == other_id
                    ]
                    interaction_matrix[member_id][other_id] = {
                        "count": len(member_interactions),
                        "total_strength": sum(i.interaction_strength for i in member_interactions),
                        "avg_strength": sum(i.interaction_strength for i in member_interactions) / len(member_interactions) if member_interactions else 0
                    }
        
        # 沈黙メンバーを特定
        silent_members = []
        for member_id in member_ids:
            # 発言回数と受信回数をカウント
            speaking_count = len([i for i in interactions if i.speaker_id == member_id])
            listening_count = len([i for i in interactions if i.listener_id == member_id])
            
            if speaking_count == 0 and listening_count > 0:
                silent_members.append({
                    "user_id": member_id,
                    "listening_count": listening_count,
                    "type": "passive_listener"
                })
            elif speaking_count == 0 and listening_count == 0:
                silent_members.append({
                    "user_id": member_id,
                    "listening_count": 0,
                    "type": "completely_silent"
                })
        
        # コミュニケーション効率を計算
        communication_efficiency = self._calculate_communication_efficiency(
            interactions, member_ids
        )
        
        # 相互作用タイプの分布を計算
        interaction_types_distribution = self._get_interaction_types_distribution(interactions)
        
        return {
            "interaction_matrix": interaction_matrix,
            "silent_members": silent_members,
            "communication_efficiency": communication_efficiency,
            "interaction_types_distribution": interaction_types_distribution
        }
    
    def _calculate_communication_efficiency(
        self, 
        interactions: List[TeamInteraction], 
        member_ids: List[int]
    ) -> float:
        """コミュニケーション効率を計算"""
        if not interactions:
            return 0.0
        
        # 実際の相互作用数
        actual_interactions = len(set((i.speaker_id, i.listener_id) for i in interactions))
        
        # 可能な相互作用数（全メンバー間の組み合わせ）
        possible_interactions = len(member_ids) * (len(member_ids) - 1)
        
        if possible_interactions == 0:
            return 0.0
        
        return actual_interactions / possible_interactions
    
    def _get_interaction_types_distribution(
        self, 
        interactions: List[TeamInteraction]
    ) -> Dict[str, int]:
        """相互作用タイプの分布を取得"""
        distribution = {}
        for interaction in interactions:
            interaction_type = interaction.interaction_type
            distribution[interaction_type] = distribution.get(interaction_type, 0) + 1
        return distribution
    
    def calculate_team_compatibility(
        self, 
        team_id: int
    ) -> TeamCompatibilityAnalysis:
        """チーム相性スコアを計算"""
        try:
            # 既存のデータをクリア
            self.db.query(TeamCompatibility).filter(
                TeamCompatibility.team_id == team_id
            ).delete()
            
            # チームメンバーを取得
            team_members = self.db.query(TeamMember).filter(
                TeamMember.team_id == team_id
            ).all()
            
            if len(team_members) < 2:
                raise ValueError("チームメンバーが2人未満です")
            
            compatibilities = []
            total_compatibility = 0.0
            compatibility_count = 0
            
            # 全メンバー間の相性を計算
            for i, member1 in enumerate(team_members):
                for j, member2 in enumerate(team_members):
                    if i < j:  # 重複を避ける
                        compatibility = self._calculate_member_compatibility(
                            member1.user_id, 
                            member2.user_id, 
                            team_id
                        )
                        
                        # 相性オブジェクトを作成
                        compatibility_obj = TeamCompatibility(
                            team_id=team_id,
                            member1_id=member1.user_id,
                            member2_id=member2.user_id,
                            communication_style_score=compatibility["communication_style_score"],
                            personality_compatibility=compatibility["personality_compatibility"],
                            work_style_score=compatibility["work_style_score"],
                            overall_compatibility=compatibility["overall_compatibility"]
                        )
                        
                        compatibilities.append(compatibility_obj)
                        total_compatibility += compatibility["overall_compatibility"]
                        compatibility_count += 1
            
            # 結果を保存
            for compatibility in compatibilities:
                self.db.add(compatibility)
            self.db.commit()
            
            # チームバランススコアを計算
            team_balance_score = total_compatibility / compatibility_count if compatibility_count > 0 else 0.0
            
            # 相性マトリックスを作成
            compatibility_matrix = self._create_compatibility_matrix(compatibilities, team_members)
            
            return TeamCompatibilityAnalysis(
                team_id=team_id,
                total_members=len(team_members),
                average_compatibility=team_balance_score,
                compatibility_matrix=compatibility_matrix,
                compatibility_details=compatibilities
            )
            
        except Exception as e:
            logger.error(f"チーム相性計算でエラーが発生: {e}")
            self.db.rollback()
            raise
    
    def _calculate_member_compatibility(
        self, 
        member1_id: int, 
        member2_id: int, 
        team_id: int
    ) -> Dict[str, float]:
        """2人のメンバー間の相性を計算"""
        # メンバープロファイルを取得
        profile1 = self.db.query(TeamMemberProfile).filter(
            TeamMemberProfile.user_id == member1_id,
            TeamMemberProfile.team_id == team_id
        ).first()
        
        profile2 = self.db.query(TeamMemberProfile).filter(
            TeamMemberProfile.user_id == member2_id,
            TeamMemberProfile.team_id == team_id
        ).first()
        
        # プロファイルが存在しない場合はデフォルト値を設定
        if not profile1 or not profile2:
            return {
                "communication_style_score": 0.5,
                "personality_compatibility": 0.5,
                "work_style_score": 0.5,
                "overall_compatibility": 0.5
            }
        
        # コミュニケーションスタイルの相性を計算
        communication_style_score = self._calculate_communication_style_compatibility(
            profile1.communication_style,
            profile2.communication_style
        )
        
        # 性格特性の相性を計算
        personality_compatibility = self._calculate_personality_compatibility(
            profile1.personality_traits,
            profile2.personality_traits
        )
        
        # 仕事スタイルの相性を計算
        work_style_score = self._calculate_work_style_compatibility(
            profile1.work_preferences,
            profile2.work_preferences
        )
        
        # 総合相性スコアを計算（重み付き平均）
        overall_compatibility = (
            communication_style_score * 0.4 +
            personality_compatibility * 0.35 +
            work_style_score * 0.25
        )
        
        return {
            "communication_style_score": communication_style_score,
            "personality_compatibility": personality_compatibility,
            "work_style_score": work_style_score,
            "overall_compatibility": overall_compatibility
        }
    
    def _calculate_communication_style_compatibility(
        self, 
        style1: Optional[str], 
        style2: Optional[str]
    ) -> float:
        """コミュニケーションスタイルの相性を計算"""
        if not style1 or not style2:
            return 0.5
        
        # コミュニケーションスタイルの相性マトリックス
        compatibility_matrix = {
            "assertive": {
                "assertive": 0.6,      # 同タイプ：中程度
                "collaborative": 0.9,  # 相補的：高
                "analytical": 0.7,     # 相補的：中高
                "supportive": 0.8      # 相補的：中高
            },
            "collaborative": {
                "assertive": 0.9,      # 相補的：高
                "collaborative": 0.8,  # 同タイプ：中高
                "analytical": 0.9,     # 相補的：高
                "supportive": 0.9      # 相補的：高
            },
            "analytical": {
                "assertive": 0.7,      # 相補的：中高
                "collaborative": 0.9,  # 相補的：高
                "analytical": 0.7,     # 同タイプ：中程度
                "supportive": 0.8      # 相補的：中高
            },
            "supportive": {
                "assertive": 0.8,      # 相補的：中高
                "collaborative": 0.9,  # 相補的：高
                "analytical": 0.8,     # 相補的：中高
                "supportive": 0.6      # 同タイプ：中程度
            }
        }
        
        return compatibility_matrix.get(style1, {}).get(style2, 0.5)
    
    def _calculate_personality_compatibility(
        self, 
        traits1: Optional[Dict], 
        traits2: Optional[Dict]
    ) -> float:
        """性格特性の相性を計算"""
        if not traits1 or not traits2:
            return 0.5
        
        # 共通の特性を特定
        common_traits = set(traits1.keys()) & set(traits2.keys())
        if not common_traits:
            return 0.5
        
        total_compatibility = 0.0
        trait_count = 0
        
        for trait in common_traits:
            value1 = traits1[trait]
            value2 = traits2[trait]
            
            # 特性値の差を計算（0-1の範囲で正規化）
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                # 数値の場合：差が小さいほど相性が良い
                diff = abs(value1 - value2)
                if diff <= 0.2:
                    compatibility = 0.9  # 非常に相性が良い
                elif diff <= 0.4:
                    compatibility = 0.7  # 相性が良い
                elif diff <= 0.6:
                    compatibility = 0.5  # 中程度
                elif diff <= 0.8:
                    compatibility = 0.3  # 相性が悪い
                else:
                    compatibility = 0.1  # 非常に相性が悪い
            else:
                # 文字列の場合：一致するかどうか
                compatibility = 1.0 if value1 == value2 else 0.3
            
            total_compatibility += compatibility
            trait_count += 1
        
        return total_compatibility / trait_count if trait_count > 0 else 0.5
    
    def _calculate_work_style_compatibility(
        self, 
        preferences1: Optional[Dict], 
        preferences2: Optional[Dict]
    ) -> float:
        """仕事スタイルの相性を計算"""
        if not preferences1 or not preferences2:
            return 0.5
        
        # 共通の設定項目を特定
        common_preferences = set(preferences1.keys()) & set(preferences2.keys())
        if not common_preferences:
            return 0.5
        
        total_compatibility = 0.0
        preference_count = 0
        
        for pref in common_preferences:
            value1 = preferences1[pref]
            value2 = preferences2[pref]
            
            # 設定値の相性を計算
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                # 数値の場合：差が小さいほど相性が良い
                diff = abs(value1 - value2)
                if diff <= 0.2:
                    compatibility = 0.9
                elif diff <= 0.4:
                    compatibility = 0.7
                elif diff <= 0.6:
                    compatibility = 0.5
                elif diff <= 0.8:
                    compatibility = 0.3
                else:
                    compatibility = 0.1
            else:
                # 文字列の場合：一致するかどうか
                compatibility = 1.0 if value1 == value2 else 0.3
            
            total_compatibility += compatibility
            preference_count += 1
        
        return total_compatibility / preference_count if preference_count > 0 else 0.5
    
    def _create_compatibility_matrix(
        self, 
        compatibilities: List[TeamCompatibility], 
        team_members: List[TeamMember]
    ) -> Dict[int, Dict[int, float]]:
        """相性マトリックスを作成"""
        matrix = {}
        member_ids = [member.user_id for member in team_members]
        
        for member_id in member_ids:
            matrix[member_id] = {}
            for other_id in member_ids:
                if member_id == other_id:
                    matrix[member_id][other_id] = 1.0  # 自分自身との相性は1.0
                else:
                    # 相性データを検索
                    compatibility = next(
                        (c for c in compatibilities 
                         if (c.member1_id == member_id and c.member2_id == other_id) or
                            (c.member1_id == other_id and c.member2_id == member_id)),
                        None
                    )
                    
                    if compatibility:
                        matrix[member_id][other_id] = compatibility.overall_compatibility
                    else:
                        matrix[member_id][other_id] = 0.5  # デフォルト値
        
        return matrix
    
    def analyze_team_cohesion(
        self, 
        team_id: int, 
        session_id: int
    ) -> TeamCohesionAnalysis:
        """チーム結束力分析を実行"""
        try:
            # 既存のデータをクリア
            self.db.query(TeamCohesion).filter(
                TeamCohesion.team_id == team_id,
                TeamCohesion.session_id == session_id
            ).delete()
            
            # 相互作用データを取得
            interactions = self.db.query(TeamInteraction).filter(
                TeamInteraction.team_id == team_id,
                TeamInteraction.session_id == session_id
            ).all()
            
            # 共通トピックを特定
            common_topics = self._identify_common_topics(interactions)
            
            # 意見の一致度を分析
            opinion_alignment = self._analyze_opinion_alignment(interactions)
            
            # 文化的形成度を評価
            cultural_formation = self._evaluate_cultural_formation(interactions)
            
            # 結束力スコアを計算
            cohesion_score = self._calculate_cohesion_score(
                interactions, opinion_alignment, cultural_formation
            )
            
            # 改善提案を生成
            improvement_suggestions = self._generate_improvement_suggestions(
                cohesion_score, interactions, opinion_alignment
            )
            
            # 結束力オブジェクトを作成
            cohesion = TeamCohesion(
                team_id=team_id,
                session_id=session_id,
                cohesion_score=cohesion_score,
                common_topics=common_topics,
                opinion_alignment=opinion_alignment,
                cultural_formation=cultural_formation,
                improvement_suggestions=improvement_suggestions
            )
            
            # 結果を保存
            self.db.add(cohesion)
            self.db.commit()
            
            return TeamCohesionAnalysis(
                team_id=team_id,
                session_id=session_id,
                cohesion_score=cohesion_score,
                common_topics=common_topics,
                opinion_alignment=opinion_alignment,
                cultural_formation=cultural_formation,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            logger.error(f"チーム結束力分析でエラーが発生: {e}")
            self.db.rollback()
            raise
    
    def _identify_common_topics(self, interactions: List[TeamInteraction]) -> List[str]:
        """共通トピックを特定"""
        # 相互作用の強度が高いものを基にトピックを特定
        strong_interactions = [i for i in interactions if i.interaction_strength > 0.7]
        
        # トピックの候補（実際の実装では音声認識結果から抽出）
        topics = []
        if strong_interactions:
            # 相互作用の種類に基づいてトピックを推測
            response_count = len([i for i in strong_interactions if i.interaction_type == "response"])
            support_count = len([i for i in strong_interactions if i.interaction_type == "support"])
            
            if response_count > support_count:
                topics.append("活発な議論")
            if support_count > 0:
                topics.append("協力的な作業")
            if len(strong_interactions) > 10:
                topics.append("深い議論")
        
        return topics if topics else ["一般的な会話"]
    
    def _analyze_opinion_alignment(self, interactions: List[TeamInteraction]) -> float:
        """意見の一致度を分析"""
        if not interactions:
            return 0.5
        
        # 相互作用の種類に基づいて意見の一致度を推測
        support_count = len([i for i in interactions if i.interaction_type == "support"])
        challenge_count = len([i for i in interactions if i.interaction_type == "challenge"])
        total_interactions = len(interactions)
        
        if total_interactions == 0:
            return 0.5
        
        # サポートが多いほど意見が一致していると判断
        support_ratio = support_count / total_interactions
        challenge_ratio = challenge_count / total_interactions
        
        # 意見一致度を計算（0.0-1.0）
        alignment_score = support_ratio * 0.8 + (1.0 - challenge_ratio) * 0.2
        
        return max(0.0, min(1.0, alignment_score))
    
    def _evaluate_cultural_formation(self, interactions: List[TeamInteraction]) -> float:
        """文化的形成度を評価"""
        if not interactions:
            return 0.5
        
        # 相互作用の多様性を評価
        interaction_types = set(i.interaction_type for i in interactions)
        type_diversity = len(interaction_types) / 4.0  # 4種類の相互作用タイプ
        
        # 相互作用の強度の平均
        avg_strength = sum(i.interaction_strength for i in interactions) / len(interactions)
        
        # 文化的形成度を計算
        cultural_score = (type_diversity * 0.6 + avg_strength * 0.4)
        
        return max(0.0, min(1.0, cultural_score))
    
    def _calculate_cohesion_score(
        self, 
        interactions: List[TeamInteraction], 
        opinion_alignment: float, 
        cultural_formation: float
    ) -> float:
        """結束力スコアを計算"""
        if not interactions:
            return 0.5
        
        # 相互作用の密度（時間あたりの相互作用数）
        if interactions:
            total_duration = sum(i.duration for i in interactions)
            interaction_density = len(interactions) / max(total_duration, 1.0)
        else:
            interaction_density = 0.0
        
        # 相互作用の強度の平均
        avg_strength = sum(i.interaction_strength for i in interactions) / len(interactions)
        
        # 結束力スコアを計算（重み付き平均）
        cohesion_score = (
            interaction_density * 0.3 +
            avg_strength * 0.3 +
            opinion_alignment * 0.25 +
            cultural_formation * 0.15
        )
        
        return max(0.0, min(1.0, cohesion_score))
    
    def _generate_improvement_suggestions(
        self, 
        cohesion_score: float, 
        interactions: List[TeamInteraction], 
        opinion_alignment: float
    ) -> str:
        """改善提案を生成"""
        suggestions = []
        
        if cohesion_score < 0.3:
            suggestions.append("チームメンバー間のコミュニケーションを促進する必要があります")
        elif cohesion_score < 0.6:
            suggestions.append("チームの結束力を向上させるための活動を検討してください")
        
        if opinion_alignment < 0.4:
            suggestions.append("意見の相違を建設的に解決するためのプロセスを確立してください")
        
        if not interactions:
            suggestions.append("チーム活動の機会を増やしてください")
        
        if suggestions:
            return "。".join(suggestions) + "。"
        else:
            return "現在のチーム結束力は良好です。この状態を維持してください。"
