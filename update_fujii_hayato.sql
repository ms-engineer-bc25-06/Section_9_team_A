-- 藤井隼人さんのプロフィール更新スクリプト
-- 実行日時: 2025-08-26
-- 対象ユーザー: test-2@example.com
-- フルネームの更新
UPDATE users
SET
  full_name = '藤井隼人'
WHERE
  email = 'test-2@example.com';

-- ユーザー名の更新
UPDATE users
SET
  username = 'Fujii Hayato'
WHERE
  email = 'test-2@example.com';

-- 更新確認
SELECT
  id,
  email,
  username,
  full_name,
  updated_at
FROM
  users
WHERE
  email = 'test-2@example.com';