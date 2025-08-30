-- フィードバック機能テスト用データ投入スクリプト
-- 実行日時: 2025-08-26
-- 1. analysesテーブルにテストデータを投入
INSERT INTO
  analyses (
    user_id,
    title,
    content,
    analysis_type,
    status,
    is_public,
    visibility_level,
    requires_approval
  )
VALUES
  -- 藤井隼人さんの分析結果
  (
    3,
    '音声分析結果 - チーム会議',
    'チーム会議での発言パターンを分析した結果です。コミュニケーションスタイルが明確になりました。',
    'voice_analysis',
    'completed',
    false,
    'private',
    true
  ),
  (
    3,
    '個人成長レポート - 2025年8月',
    '今月の活動を通じて得られた成長ポイントと改善点をまとめました。',
    'growth_analysis',
    'completed',
    false,
    'private',
    true
  ),
  (
    3,
    'チームダイナミクス分析',
    'チーム内での相互作用パターンを分析し、改善提案を作成しました。',
    'team_dynamics',
    'completed',
    false,
    'team',
    true
  ),
  -- 他のユーザーの分析結果
  (
    1,
    '管理者向け分析レポート',
    'システム全体の利用状況とパフォーマンス分析結果です。',
    'system_analysis',
    'completed',
    true,
    'organization',
    false
  ),
  (
    6,
    'えりかの音声分析',
    'ペルソナユーザーとしての音声パターンを分析しました。',
    'voice_analysis',
    'completed',
    false,
    'private',
    true
  ),
  (
    7,
    'うっちーの成長分析',
    '個人の成長軌跡を時系列で分析した結果です。',
    'growth_analysis',
    'completed',
    false,
    'private',
    true
  );

-- 2. feedback_approvalsテーブルにテストデータを投入
INSERT INTO
  feedback_approvals (
    analysis_id,
    requester_id,
    reviewer_id,
    approval_status,
    visibility_level,
    request_reason,
    review_notes,
    rejection_reason,
    is_confirmed
  )
VALUES
  -- 藤井隼人さんの承認リクエスト（承認済み）
  (
    1,
    3,
    1,
    'approved',
    'private',
    '個人の成長のために分析結果を確認したい',
    '詳細な分析が素晴らしいです。承認します。',
    NULL,
    true
  ),
  (
    2,
    3,
    1,
    'approved',
    'private',
    '自己改善の参考にしたい',
    '成長ポイントが明確に整理されています。承認します。',
    NULL,
    true
  ),
  -- 藤井隼人さんの承認リクエスト（修正必要）
  (
    3,
    3,
    1,
    'requires_changes',
    'team',
    'チーム内で共有したい分析結果です',
    'データの検証が必要です。修正後に再提出してください。',
    NULL,
    false
  ),
  -- 他のユーザーの承認リクエスト（承認待ち）
  (
    4,
    1,
    NULL,
    'pending',
    'organization',
    '組織全体での共有を希望',
    NULL,
    NULL,
    false
  ),
  (
    5,
    6,
    1,
    'under_review',
    'private',
    '個人の改善に活用したい',
    NULL,
    NULL,
    false
  ),
  -- 却下された例
  (
    6,
    7,
    1,
    'rejected',
    'private',
    '成長の記録として残したい',
    NULL,
    'プライバシー設定の確認が必要です。',
    false
  );

-- 3. 確認用クエリ
-- 投入されたデータの確認
SELECT
  'analyses' as table_name,
  COUNT(*) as count
FROM
  analyses
UNION ALL
SELECT
  'feedback_approvals' as table_name,
  COUNT(*) as count
FROM
  feedback_approvals;

-- 藤井隼人さんの承認状況確認
SELECT
  a.title,
  fa.approval_status,
  fa.review_notes,
  fa.rejection_reason,
  fa.requested_at
FROM
  feedback_approvals fa
  JOIN analyses a ON fa.analysis_id = a.id
WHERE
  fa.requester_id = 3
ORDER BY
  fa.requested_at DESC;