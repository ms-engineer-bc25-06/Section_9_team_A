-- 現在のデータベースの状態をエクスポートするSQLスクリプト
-- このファイルを実行することで、他のメンバーも同じデータベース状態を再現できます

-- usersテーブルのデータをエクスポート
INSERT INTO users (
    id, email, username, full_name, avatar_url, bio, nickname, department, 
    join_date, birth_date, hometown, residence, hobbies, student_activities, 
    holiday_activities, favorite_food, favorite_media, favorite_music, 
    pets_oshi, respected_person, motto, future_goals, firebase_uid, 
    hashed_password, has_temporary_password, temporary_password, 
    temporary_password_expires_at, is_first_login, is_active, is_verified, 
    is_admin, created_at, updated_at, last_login_at, last_password_change_at
) VALUES 
-- 管理者ユーザー
(3, 'admin@example.com', 'admin@example.com', 'admin@example.com', NULL, NULL, NULL, '管理部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'g7lzX9SnUUeBpRAae9CjynV0CX43', NULL, false, NULL, NULL, false, true, true, true, '2025-08-07 15:10:04.209049+00', '2025-08-07 15:10:04.209049+00', '2025-08-26 12:07:24.195419+00', '2025-08-22 00:49:48.853568+00'),

-- テストユーザー
(85, 'test-4@example.com', 'test-4', '橘しおり', NULL, NULL, NULL, '経理部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'dev_uid_1004', NULL, false, NULL, NULL, false, true, false, false, '2025-08-21 16:28:04.777904+00', '2025-08-21 16:28:04.777904+00', '2025-08-26 12:06:40.708691+00', '2025-08-26 12:03:21.450048+00'),
(86, 'test-1@example.com', 'test-1', '宮崎大輝', NULL, NULL, NULL, '企画部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'dev_uid_1001', NULL, false, NULL, NULL, false, true, false, false, '2025-08-22 00:23:41.288980+00', '2025-08-22 00:23:41.288980+00', '2025-08-26 12:05:20.737684+00', '2025-08-26 12:03:21.452446+00'),
(87, 'test-2@example.com', 'test-2', '藤井隼人', NULL, NULL, NULL, '人事部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'dev_uid_1002', NULL, false, NULL, NULL, false, true, false, false, '2025-08-22 01:08:25.142359+00', '2025-08-22 01:08:25.142359+00', '2025-08-26 11:52:52.923510+00', '2025-08-26 12:03:21.455344+00'),
(88, 'test-3@example.com', 'test-3', '真田梨央', NULL, NULL, NULL, '経理部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'dev_uid_1003', NULL, false, NULL, NULL, false, true, false, false, '2025-08-22 02:24:25.469360+00', '2025-08-22 02:24:25.469360+00', '2025-08-26 12:05:49.600979+00', '2025-08-26 12:03:21.443789+00'),

-- bridgeline.comドメインのユーザー
(89, 'asuka@bridgeline.com', 'asuka', '野口 明日香', NULL, NULL, NULL, '企画部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'thlwiFkQjgSycs2rglUZoHGThGh1', NULL, false, NULL, NULL, false, true, false, false, '2025-08-22 11:05:21.129489+00', '2025-08-22 11:05:21.129489+00', '2025-08-26 11:53:34.020619+00', '2025-08-22 11:06:23.464436+00'),
(90, 'rui@bridgeline.com', 'rui', '大村 瑠衣', NULL, NULL, NULL, '企画部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'sIqTdUd3VlOkcPISFvD8i589y3h1', NULL, false, NULL, NULL, false, true, false, false, '2025-08-23 06:27:13.878950+00', '2025-08-23 06:27:13.878950+00', '2025-08-23 06:27:54.773115+00', '2025-08-23 06:28:13.931187+00'),
(91, 'shizuka@bridgeline.com', 'shizuka', '渡部 志津香', NULL, NULL, NULL, '企画部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'l97JVsZdEVSXvUB6491Q1LoqXSB2', NULL, false, NULL, NULL, false, true, false, false, '2025-08-23 06:29:32.246651+00', '2025-08-23 06:29:32.246651+00', '2025-08-23 06:30:09.450427+00', '2025-08-23 06:30:27.195758+00'),
(92, 'kodai@bridgeline.com', 'kodai', '朝宮優', NULL, NULL, NULL, '企画部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '3UfJ2s2YDuNpHVyj6OKQqn43KhH2', NULL, false, NULL, NULL, false, true, false, false, '2025-08-23 06:34:31.908498+00', '2025-08-23 06:34:31.908498+00', '2025-08-23 06:38:18.482382+00', '2025-08-26 12:03:21.453980+00'),
(93, 'erika@bridgeline.com', 'erika', '中川 えりか', NULL, NULL, NULL, '企画部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'rI5UNAAjEBOrOSDq7M1j7ruQxRC3', NULL, false, NULL, NULL, false, true, false, false, '2025-08-23 06:35:15.896493+00', '2025-08-23 06:35:15.896493+00', '2025-08-23 06:39:19.939185+00', '2025-08-23 06:39:33.934794+00'),
(94, 'ucchi@bridgeline.com', 'ucchi', '加瀬賢一郎', NULL, NULL, NULL, '人事部', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'zmTn7PmUC6Yjmn78GdM9qrkoPhq2', NULL, false, NULL, NULL, false, true, false, false, '2025-08-23 06:35:55.864464+00', '2025-08-23 06:35:55.864464+00', '2025-08-25 05:03:04.359495+00', '2025-08-26 12:03:21.456812+00')

ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    username = EXCLUDED.username,
    full_name = EXCLUDED.full_name,
    department = EXCLUDED.department,
    firebase_uid = EXCLUDED.firebase_uid,
    has_temporary_password = EXCLUDED.has_temporary_password,
    is_first_login = EXCLUDED.is_first_login,
    is_active = EXCLUDED.is_active,
    is_admin = EXCLUDED.is_admin,
    updated_at = EXCLUDED.updated_at,
    last_login_at = EXCLUDED.last_login_at,
    last_password_change_at = EXCLUDED.last_password_change_at;
