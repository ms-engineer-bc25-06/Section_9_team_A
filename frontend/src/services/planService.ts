// プラン管理サービス
export interface PlanFeatures {
  max_team_members: number | 'unlimited';
  max_sessions_per_month: number | 'unlimited';
  max_minutes_per_month: number | 'unlimited';
  transcription_included: boolean;
  basic_ai_analysis: boolean;
  advanced_ai_analysis: boolean;
  custom_reports: boolean;
  api_access: boolean;
  sso_integration: boolean;
  storage_gb: number | 'unlimited';
  support_level: 'email' | 'chat' | 'phone';
}

export interface Plan {
  id: string;
  name: string;
  monthly_price: number;
  yearly_price: number;
  features: PlanFeatures;
  trial_days: number;
  custom_pricing?: boolean;
}

export const PLANS: Record<string, Plan> = {
  basic: {
    id: 'basic',
    name: 'Basic Plan',
    monthly_price: 980,
    yearly_price: 9800,
    features: {
      max_team_members: 10,
      max_sessions_per_month: 50,
      max_minutes_per_month: 3000,
      transcription_included: true,
      basic_ai_analysis: true,
      advanced_ai_analysis: false,
      custom_reports: false,
      api_access: false,
      sso_integration: false,
      storage_gb: 2,
      support_level: 'email'
    },
    trial_days: 14
  },
  premium: {
    id: 'premium',
    name: 'Premium Plan',
    monthly_price: 2980,
    yearly_price: 29800,
    features: {
      max_team_members: 50,
      max_sessions_per_month: 200,
      max_minutes_per_month: 12000,
      transcription_included: true,
      basic_ai_analysis: true,
      advanced_ai_analysis: true,
      custom_reports: true,
      api_access: false,
      sso_integration: false,
      storage_gb: 10,
      support_level: 'chat'
    },
    trial_days: 14
  },
  enterprise: {
    id: 'enterprise',
    name: 'Enterprise Plan',
    monthly_price: 9800,
    yearly_price: 98000,
    features: {
      max_team_members: 'unlimited',
      max_sessions_per_month: 'unlimited',
      max_minutes_per_month: 'unlimited',
      transcription_included: true,
      basic_ai_analysis: true,
      advanced_ai_analysis: true,
      custom_reports: true,
      api_access: true,
      sso_integration: true,
      storage_gb: 'unlimited',
      support_level: 'phone'
    },
    trial_days: 30,
    custom_pricing: true
  }
};

export class PlanService {
  /**
   * プラン情報を取得
   */
  static getPlan(planId: string): Plan | null {
    return PLANS[planId] || null;
  }

  /**
   * 全プラン一覧を取得
   */
  static getAllPlans(): Plan[] {
    return Object.values(PLANS);
  }

  /**
   * ユーザー数に基づいてプランを決定
   */
  static getCurrentPlanByUserCount(userCount: number): string {
    if (userCount <= 10) return 'basic'
    if (userCount <= 50) return 'premium'
    return 'enterprise'
  }

  /**
   * 年額プランの割引価格を計算
   */
  static calculateYearlyPrice(monthlyPrice: number, discountRate: number = 0.2): number {
    return Math.round(monthlyPrice * 12 * (1 - discountRate));
  }

  /**
   * 月額換算価格を計算
   */
  static calculateMonthlyEquivalent(yearlyPrice: number): number {
    return Math.round(yearlyPrice / 12);
  }

  /**
   * プランの利用状況をチェック
   */
  static checkPlanUsage(currentUsers: number, planId: string): {
    isOverLimit: boolean;
    excessUsers: number;
    maxUsers: number;
  } {
    const plan = this.getPlan(planId);
    if (!plan) {
      return { isOverLimit: false, excessUsers: 0, maxUsers: 0 };
    }

    const maxUsers = plan.features.max_team_members === 'unlimited' 
      ? Number.MAX_SAFE_INTEGER 
      : plan.features.max_team_members;

    const isOverLimit = currentUsers > maxUsers;
    const excessUsers = isOverLimit ? currentUsers - maxUsers : 0;

    return { isOverLimit, excessUsers, maxUsers };
  }

  /**
   * プランの料金を取得
   */
  static getPlanPrice(planId: string, billingCycle: 'monthly' | 'yearly'): number {
    const plan = this.getPlan(planId);
    if (!plan) return 0;

    if (billingCycle === 'yearly') {
      return this.calculateYearlyPrice(plan.monthly_price);
    }
    return plan.monthly_price;
  }

  /**
   * プランの表示用情報を取得
   */
  static getPlanDisplayInfo(planId: string): {
    name: string;
    monthlyPrice: number;
    yearlyPrice: number;
    monthlyEquivalent: number;
    maxUsers: string;
    maxSessions: string;
    features: string[];
  } {
    const plan = this.getPlan(planId);
    if (!plan) {
      return {
        name: 'Unknown Plan',
        monthlyPrice: 0,
        yearlyPrice: 0,
        monthlyEquivalent: 0,
        maxUsers: '0',
        maxSessions: '0',
        features: []
      };
    }

    const yearlyPrice = this.calculateYearlyPrice(plan.monthly_price);
    const monthlyEquivalent = this.calculateMonthlyEquivalent(yearlyPrice);

    const features = [];
    if (plan.features.transcription_included) features.push('文字起こし機能');
    if (plan.features.basic_ai_analysis) features.push('基本AI分析');
    if (plan.features.advanced_ai_analysis) features.push('高度AI分析');
    if (plan.features.custom_reports) features.push('カスタムレポート');
    if (plan.features.api_access) features.push('API アクセス');
    if (plan.features.sso_integration) features.push('SSO連携');

    return {
      name: plan.name,
      monthlyPrice: plan.monthly_price,
      yearlyPrice,
      monthlyEquivalent,
      maxUsers: plan.features.max_team_members === 'unlimited' 
        ? '無制限' 
        : `${plan.features.max_team_members}名`,
      maxSessions: plan.features.max_sessions_per_month === 'unlimited'
        ? '無制限'
        : `${plan.features.max_sessions_per_month}セッション/月`,
      features
    };
  }
}
