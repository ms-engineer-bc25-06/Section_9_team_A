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


class TeamDynamicsService:
    """チームダイナミクス分析サービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_team_interactions(
        self, 
        team_id: int, 
        session_id: int,
        transcriptions: List[Transcription]
    ) -> Dict:
        """
        チーム相互作用パターン分析
        
        Args:
            team_id: チームID
            session_id: 音声セッションID
            transcriptions: 文字起こしデータのリスト
            
        Returns:
            相互作用分析結果
        """
        # 既存の相互作用データをクリア
        self.db.query(TeamInteraction).filter(
            and_(TeamInteraction.team_id == team_id, 
                 TeamInteraction.session_id == session_id)
        ).delete()
        
        # 相互作用パターンを分析
        interactions = self._analyze_interaction_patterns(transcriptions)
        
        # 相互作用データを保存
        for interaction in interactions:
            db_interaction = TeamInteraction(
                team_id=team_id,
                session_id=session_id,
                speaker_id=interaction['speaker_id'],
                listener_id=interaction['listener_id'],
                interaction_type=interaction['type'],
                interaction_strength=interaction['strength'],
                duration=interaction['duration']
            )
            self.db.add(db_interaction)
        
        self.db.commit()
        
        # 分析結果を計算
        return self._calculate_interaction_metrics(team_id, session_id)
    
    def _analyze_interaction_patterns(
        self, 
        transcriptions: List[Transcription]
    ) -> List[Dict]:
        """相互作用パターンを分析"""
        interactions = []
        
        # 発言者ごとの発言時間を計算
        speaker_times = {}
        for trans in transcriptions:
            if trans.user_id not in speaker_times:
                speaker_times[trans.user_id] = 0
            speaker_times[trans.user_id] += trans.duration or 0
        
        # 発言者間の相互作用を分析
        for i, trans1 in enumerate(transcriptions):
            if i == 0:
                continue
                
            prev_trans = transcriptions[i-1]
            
            # 前の発言者との相互作用を分析
            if prev_trans.user_id != trans1.user_id:
                interaction_type = self._determine_interaction_type(
                    prev_trans, trans1
                )
                
                interaction = {
                    'speaker_id': trans1.user_id,
                    'listener_id': prev_trans.user_id,
                    'type': interaction_type,
                    'strength': self._calculate_interaction_strength(
                        prev_trans, trans1
                    ),
                    'duration': trans1.duration or 0
                }
                interactions.append(interaction)
        
        return interactions
    
    def _determine_interaction_type(
        self, 
        prev_trans: Transcription, 
        curr_trans: Transcription
    ) -> str:
        """相互作用タイプを判定"""
        # 時間間隔を計算
        time_gap = (curr_trans.timestamp - prev_trans.timestamp).total_seconds()
        
        if time_gap < 1.0:
            return 'interruption'  # 割り込み
        elif time_gap < 3.0:
            return 'response'  # 即座の反応
        elif time_gap < 10.0:
            return 'support'  # サポート
        else:
            return 'challenge'  # 挑戦・質問
    
    def _calculate_interaction_strength(
        self, 
        prev_trans: Transcription, 
        curr_trans: Transcription
    ) -> float:
        """相互作用の強度を計算"""
        # 時間間隔に基づく強度
        time_gap = (curr_trans.timestamp - prev_trans.timestamp).total_seconds()
        
        if time_gap < 1.0:
            return 0.9  # 割り込みは強い相互作用
        elif time_gap < 3.0:
            return 0.7  # 即座の反応
        elif time_gap < 10.0:
            return 0.5  # サポート
        else:
            return 0.3  # 時間が空いた反応
    
    def _calculate_interaction_metrics(
        self, 
        team_id: int, 
        session_id: int
    ) -> Dict:
        """相互作用メトリクスを計算"""
        interactions = self.db.query(TeamInteraction).filter(
            and_(TeamInteraction.team_id == team_id, 
                 TeamInteraction.session_id == session_id)
        ).all()
        
        if not interactions:
            return {}
        
        # 相互作用マトリックスを作成
        interaction_matrix = {}
        total_interactions = len(interactions)
        
        for interaction in interactions:
            key = f"{interaction.speaker_id}_{interaction.listener_id}"
            if key not in interaction_matrix:
                interaction_matrix[key] = {
                    'count': 0,
                    'total_strength': 0,
                    'types': {}
                }
            
            interaction_matrix[key]['count'] += 1
            interaction_matrix[key]['total_strength'] += interaction.interaction_strength
            
            if interaction.interaction_type not in interaction_matrix[key]['types']:
                interaction_matrix[key]['types'][interaction.interaction_type] = 0
            interaction_matrix[key]['types'][interaction.interaction_type] += 1
        
        # 沈黙メンバーを特定
        team_members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()
        
        active_members = set()
        for interaction in interactions:
            active_members.add(interaction.speaker_id)
            active_members.add(interaction.listener_id)
        
        silent_members = [
            member.user_id for member in team_members 
            if member.user_id not in active_members
        ]
        
        # 情報伝達効率を計算
        efficiency_score = self._calculate_communication_efficiency(
            interactions, team_members
        )
        
        return {
            'interaction_matrix': interaction_matrix,
            'total_interactions': total_interactions,
            'silent_members': silent_members,
            'communication_efficiency': efficiency_score,
            'interaction_types_distribution': self._get_interaction_types_distribution(interactions)
        }
    
    def _calculate_communication_efficiency(
        self, 
        interactions: List[TeamInteraction], 
        team_members: List
    ) -> float:
        """コミュニケーション効率を計算"""
        if not interactions or not team_members:
            return 0.0
        
        member_count = len(team_members)
        total_possible_interactions = member_count * (member_count - 1)
        
        if total_possible_interactions == 0:
            return 0.0
        
        # 実際の相互作用の多様性を評価
        unique_interactions = set()
        for interaction in interactions:
            key = f"{interaction.speaker_id}_{interaction.listener_id}"
            unique_interactions.add(key)
        
        # 効率スコア = 実際の相互作用数 / 可能な相互作用数
        efficiency = len(unique_interactions) / total_possible_interactions
        
        return min(efficiency * 100, 100.0)  # 0-100のスコアに変換
    
    def _get_interaction_types_distribution(
        self, 
        interactions: List[TeamInteraction]
    ) -> Dict[str, int]:
        """相互作用タイプの分布を取得"""
        distribution = {}
        for interaction in interactions:
            if interaction.interaction_type not in distribution:
                distribution[interaction.interaction_type] = 0
            distribution[interaction.interaction_type] += 1
        return distribution
    
    def calculate_team_compatibility(
        self, 
        team_id: int
    ) -> Dict:
        """
        チーム相性スコアを算出
        
        Args:
            team_id: チームID
            
        Returns:
            相性分析結果
        """
        team_members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()
        
        if len(team_members) < 2:
            return {'error': 'チームメンバーが不足しています'}
        
        # 既存の相性データをクリア
        self.db.query(TeamCompatibility).filter(
            TeamCompatibility.team_id == team_id
        ).delete()
        
        compatibilities = []
        
        # 全メンバー間の相性を計算
        for i, member1 in enumerate(team_members):
            for j, member2 in enumerate(team_members):
                if i >= j:  # 重複を避ける
                    continue
                
                compatibility = self._calculate_member_compatibility(
                    member1.user_id, member2.user_id, team_id
                )
                
                # データベースに保存
                db_compatibility = TeamCompatibility(
                    team_id=team_id,
                    member1_id=member1.user_id,
                    member2_id=member2.user_id,
                    communication_style_score=compatibility['communication_style'],
                    personality_compatibility=compatibility['personality'],
                    work_style_score=compatibility['work_style'],
                    overall_compatibility=compatibility['overall']
                )
                self.db.add(db_compatibility)
                compatibilities.append(compatibility)
        
        self.db.commit()
        
        return {
            'compatibilities': compatibilities,
            'team_balance_score': self._calculate_team_balance_score(compatibilities),
            'compatibility_matrix': self._create_compatibility_matrix(team_members, compatibilities)
        }
    
    def _calculate_member_compatibility(
        self, 
        user1_id: int, 
        user2_id: int, 
        team_id: int
    ) -> Dict:
        """2人のメンバー間の相性を計算"""
        # ユーザープロファイルを取得
        profile1 = self.db.query(TeamMemberProfile).filter(
            and_(TeamMemberProfile.user_id == user1_id, 
                 TeamMemberProfile.team_id == team_id)
        ).first()
        
        profile2 = self.db.query(TeamMemberProfile).filter(
            and_(TeamMemberProfile.user_id == user2_id, 
                 TeamMemberProfile.team_id == team_id)
        ).first()
        
        # デフォルト値を使用（プロファイルが存在しない場合）
        comm_style1 = profile1.communication_style if profile1 else 'collaborative'
        comm_style2 = profile2.communication_style if profile2 else 'collaborative'
        
        # コミュニケーションスタイル相性
        comm_score = self._calculate_communication_style_compatibility(
            comm_style1, comm_style2
        )
        
        # 性格特性相補性（簡易版）
        personality_score = self._calculate_personality_compatibility(
            profile1, profile2
        )
        
        # 作業スタイル相性
        work_score = self._calculate_work_style_compatibility(
            profile1, profile2
        )
        
        # 総合相性スコア
        overall = (comm_score + personality_score + work_score) / 3
        
        return {
            'communication_style': comm_score,
            'personality': personality_score,
            'work_style': work_score,
            'overall': overall
        }
    
    def _calculate_communication_style_compatibility(
        self, 
        style1: str, 
        style2: str
    ) -> float:
        """コミュニケーションスタイル相性を計算"""
        # 相性マトリックス
        compatibility_matrix = {
            'assertive': {'assertive': 60, 'passive': 80, 'collaborative': 90, 'competitive': 40},
            'passive': {'assertive': 80, 'passive': 70, 'collaborative': 85, 'competitive': 75},
            'collaborative': {'assertive': 90, 'passive': 85, 'collaborative': 95, 'competitive': 60},
            'competitive': {'assertive': 40, 'passive': 75, 'competitive': 60, 'collaborative': 60}
        }
        
        return compatibility_matrix.get(style1, {}).get(style2, 50)
    
    def _calculate_personality_compatibility(
        self, 
        profile1: Optional[TeamMemberProfile], 
        profile2: Optional[TeamMemberProfile]
    ) -> float:
        """性格特性相補性を計算"""
        # 簡易版：プロファイルが存在しない場合はデフォルト値
        if not profile1 or not profile2:
            return 70.0
        
        # 性格特性の相補性を計算（実際の実装ではより詳細な分析が必要）
        traits1 = profile1.personality_traits or []
        traits2 = profile2.personality_traits or []
        
        if not traits1 or not traits2:
            return 70.0
        
        # 共通特性と相補特性を評価
        common_traits = set(traits1) & set(traits2)
        complementary_traits = len(traits1) + len(traits2) - len(common_traits)
        
        # 相補性スコアを計算
        score = (len(common_traits) * 0.3 + complementary_traits * 0.7) * 10
        return min(score, 100.0)
    
    def _calculate_work_style_compatibility(
        self, 
        profile1: Optional[TeamMemberProfile], 
        profile2: Optional[TeamMemberProfile]
    ) -> float:
        """作業スタイル相性を計算"""
        # 簡易版：プロファイルが存在しない場合はデフォルト値
        if not profile1 or not profile2:
            return 75.0
        
        # 作業環境の好みの相性を計算
        prefs1 = profile1.work_preferences or {}
        prefs2 = profile2.work_preferences or {}
        
        if not prefs1 or not prefs2:
            return 75.0
        
        # 共通の好みを評価
        common_prefs = 0
        total_prefs = 0
        
        for key in set(prefs1.keys()) | set(prefs2.keys()):
            if key in prefs1 and key in prefs2:
                if prefs1[key] == prefs2[key]:
                    common_prefs += 1
                total_prefs += 1
        
        if total_prefs == 0:
            return 75.0
        
        compatibility = (common_prefs / total_prefs) * 100
        return compatibility
    
    def _calculate_team_balance_score(
        self, 
        compatibilities: List[Dict]
    ) -> float:
        """チーム全体のバランススコアを計算"""
        if not compatibilities:
            return 0.0
        
        overall_scores = [comp['overall'] for comp in compatibilities]
        return sum(overall_scores) / len(overall_scores)
    
    def _create_compatibility_matrix(
        self, 
        team_members: List, 
        compatibilities: List[Dict]
    ) -> Dict:
        """相性マトリックスを作成"""
        matrix = {}
        
        for member in team_members:
            matrix[member.user_id] = {}
            for other_member in team_members:
                if member.user_id == other_member.user_id:
                    matrix[member.user_id][other_member.user_id] = 100  # 自分自身
                else:
                    # 相性データを検索
                    compatibility = next(
                        (comp for comp in compatibilities 
                         if (comp.get('member1_id') == member.user_id and 
                             comp.get('member2_id') == other_member.user_id) or
                            (comp.get('member1_id') == other_member.user_id and 
                             comp.get('member2_id') == member.user_id)),
                        None
                    )
                    
                    if compatibility:
                        matrix[member.user_id][other_member.user_id] = compatibility['overall']
                    else:
                        matrix[member.user_id][other_member.user_id] = 50  # デフォルト値
        
        return matrix
    
    def analyze_team_cohesion(
        self, 
        team_id: int, 
        session_id: int,
        transcriptions: List[Transcription]
    ) -> Dict:
        """
        チーム結束力分析
        
        Args:
            team_id: チームID
            session_id: 音声セッションID
            transcriptions: 文字起こしデータのリスト
            
        Returns:
            結束力分析結果
        """
        # 既存の結束力データをクリア
        self.db.query(TeamCohesion).filter(
            and_(TeamCohesion.team_id == team_id, 
                 TeamCohesion.session_id == session_id)
        ).delete()
        
        # 共通トピックを特定
        common_topics = self._identify_common_topics(transcriptions)
        
        # 意見の一致度を分析
        opinion_alignment = self._analyze_opinion_alignment(transcriptions)
        
        # チーム文化形成度を評価
        cultural_formation = self._evaluate_cultural_formation(
            team_id, session_id, transcriptions
        )
        
        # 結束力スコアを計算
        cohesion_score = (
            len(common_topics) * 20 +  # 共通トピック数
            opinion_alignment * 0.4 +   # 意見一致度
            cultural_formation * 0.4    # 文化形成度
        )
        cohesion_score = min(cohesion_score, 100.0)
        
        # 改善提案を生成
        improvement_suggestions = self._generate_improvement_suggestions(
            cohesion_score, common_topics, opinion_alignment, cultural_formation
        )
        
        # データベースに保存
        db_cohesion = TeamCohesion(
            team_id=team_id,
            session_id=session_id,
            cohesion_score=cohesion_score,
            common_topics=common_topics,
            opinion_alignment=opinion_alignment,
            cultural_formation=cultural_formation,
            improvement_suggestions=improvement_suggestions
        )
        self.db.add(db_cohesion)
        self.db.commit()
        
        return {
            'cohesion_score': cohesion_score,
            'common_topics': common_topics,
            'opinion_alignment': opinion_alignment,
            'cultural_formation': cultural_formation,
            'improvement_suggestions': improvement_suggestions
        }
    
    def _identify_common_topics(
        self, 
        transcriptions: List[Transcription]
    ) -> List[str]:
        """共通トピックを特定"""
        # 簡易版：キーワードベースの分析
        all_text = ' '.join([t.content or '' for t in transcriptions])
        
        # 一般的なビジネストピックキーワード
        business_keywords = [
            'プロジェクト', 'タスク', '期限', '目標', '成果', '問題', '解決',
            'アイデア', '提案', '改善', '効率', '品質', '顧客', '市場',
            '戦略', '計画', '実行', '評価', 'フィードバック', '学習'
        ]
        
        common_topics = []
        for keyword in business_keywords:
            if keyword in all_text:
                common_topics.append(keyword)
        
        return common_topics[:5]  # 上位5件を返す
    
    def _analyze_opinion_alignment(
        self, 
        transcriptions: List[Transcription]
    ) -> float:
        """意見の一致度を分析"""
        if not transcriptions:
            return 0.0
        
        # 簡易版：感情分析に基づく意見一致度
        positive_words = ['良い', '素晴らしい', '賛成', '同意', '支持', '良いアイデア']
        negative_words = ['悪い', '問題', '反対', '不同意', '懸念', '改善が必要']
        
        positive_count = 0
        negative_count = 0
        
        for trans in transcriptions:
            content = trans.content or ''
            for word in positive_words:
                if word in content:
                    positive_count += 1
            for word in negative_words:
                if word in content:
                    negative_count += 1
        
        total_opinions = positive_count + negative_count
        if total_opinions == 0:
            return 50.0  # デフォルト値
        
        # 意見の一致度を計算（ポジティブな意見が多いほど一致度が高い）
        alignment = (positive_count / total_opinions) * 100
        return alignment
    
    def _evaluate_cultural_formation(
        self, 
        team_id: int, 
        session_id: int, 
        transcriptions: List[Transcription]
    ) -> float:
        """チーム文化形成度を評価"""
        if not transcriptions:
            return 0.0
        
        # 相互作用の質と量を評価
        interactions = self.db.query(TeamInteraction).filter(
            and_(TeamInteraction.team_id == team_id, 
                 TeamInteraction.session_id == session_id)
        ).all()
        
        if not interactions:
            return 30.0  # 相互作用がない場合は低いスコア
        
        # 相互作用の多様性を評価
        interaction_types = set(interaction.interaction_type for interaction in interactions)
        type_diversity = len(interaction_types) / 4 * 100  # 4種類の相互作用タイプ
        
        # 相互作用の強度を評価
        avg_strength = sum(interaction.interaction_strength for interaction in interactions) / len(interactions)
        strength_score = avg_strength * 100
        
        # 文化形成度を計算
        cultural_score = (type_diversity + strength_score) / 2
        return min(cultural_score, 100.0)
    
    def _generate_improvement_suggestions(
        self, 
        cohesion_score: float, 
        common_topics: List[str], 
        opinion_alignment: float, 
        cultural_formation: float
    ) -> str:
        """改善提案を生成"""
        suggestions = []
        
        if cohesion_score < 50:
            suggestions.append("チームの結束力を高めるため、定期的なチームビルディング活動を実施してください。")
        
        if len(common_topics) < 3:
            suggestions.append("共通の関心事や目標について話し合う機会を増やしてください。")
        
        if opinion_alignment < 60:
            suggestions.append("意見の相違がある場合は、建設的な議論を通じて合意形成を図ってください。")
        
        if cultural_formation < 60:
            suggestions.append("チーム内での相互作用を促進し、共通の価値観や文化を育んでください。")
        
        if not suggestions:
            suggestions.append("現在のチーム結束力は良好です。この状態を維持してください。")
        
        return "。".join(suggestions)
