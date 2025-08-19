"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet } from "@/lib/apiClient";
import type { TeamDetailResponse, TeamsListResponse, TeamMember, UserDetailResponse } from "@/types/team";

// 必須条件を「名前＋部署」に変更（アイコンは任意）
function hasRequired(m: TeamMember): boolean {
  const nameOk = !!(m.display_name && m.display_name.trim());
  const deptOk = !!(m.profile?.department && m.profile?.department?.trim());
  return nameOk && deptOk;
}

function initialOf(name?: string) {
  const n = (name || "").trim();
  return n ? n[0] : "？";
}

export function TeamMemberList() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        // 所属チーム → 先頭のチーム
        const teams = await apiGet<TeamsListResponse>("/teams");
        const firstTeamId = teams.teams?.[0]?.id;
        if (!firstTeamId) { setMembers([]); return; }

        // チーム詳細から members を取得（無ければ /members をフォールバック）
        const detail = await apiGet<TeamDetailResponse>(`/teams/${firstTeamId}`);
        let raw: TeamMember[] = Array.isArray(detail.members) ? detail.members : [];

        if (!raw.length) {
          try {
            const res = await apiGet<{ members?: TeamMember[] }>(`/teams/${firstTeamId}/members`);
            raw = Array.isArray(res.members) ? res.members : (Array.isArray(res as any) ? (res as any) : []);
          } catch {}
        }

        // 必須が欠けている人は /users/{id} で補完（N+1だが件数は通常少）
        const enriched = await Promise.all(
          raw.map(async (m) => {
            if (hasRequired(m)) return m;
            try {
              const u = await apiGet<UserDetailResponse>(`/users/${m.id}`);
              return {
                ...m,
                display_name: m.display_name || u.display_name,
                // アイコンは任意だが、もしユーザー詳細にあれば拾っておく
                avatar_url: m.avatar_url ?? u.avatar_url,
                profile: { ...(m.profile ?? {}), ...(u.profile ?? {}) },
              };
            } catch {
              return m;
            }
          })
        );

        const filtered = enriched.filter(hasRequired);
        setMembers(filtered);
      } catch (e: any) {
        setErr(e?.message ?? "メンバー取得に失敗しました。");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="text-sm text-gray-600">読み込み中…</div>;
  if (err) return <div className="text-sm text-red-600">{err}</div>;
  if (!members.length) {
    return (
      <div className="text-sm text-gray-600">
        表示できるメンバーがいません。（※ 一覧は「名前・部署」が登録済みのメンバーのみ表示します）
      </div>
    );
  }

  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {members.map((m) => (
        <li
          key={m.id}
          className="rounded-2xl bg-white shadow p-4 border flex items-center gap-3"
        >
          {/* アイコン（任意・未登録時は頭文字） */}
          {m.avatar_url ? (
            <img
              src={m.avatar_url}
              alt={`${m.display_name}のアイコン`}
              className="h-10 w-10 rounded-full object-cover border"
            />
          ) : (
            <div className="h-10 w-10 rounded-full border grid place-items-center text-sm text-gray-600 bg-gray-50">
              {initialOf(m.display_name)}
            </div>
          )}

          {/* 名前・部署（必須） */}
          <div className="min-w-0 flex-1">
            <div className="font-semibold text-gray-900 truncate">
              {m.display_name}
            </div>
            <div className="text-sm text-gray-600 truncate">
              {m.profile!.department}
            </div>
          </div>

          {/* 詳細へ */}
          <Link
            href={`/team/${m.id}`}
            className="ml-auto inline-flex items-center rounded-xl border px-3 py-1 text-sm hover:bg-gray-50 shrink-0"
          >
            詳細
          </Link>
        </li>
      ))}
    </ul>
  );
}


//// mockデータ＆ステータス
// const mockMembers = [
//   {
//     id: 1,
//     name: "田中太郎",
//     department: "開発部",
//     // joinDate: "2023-04-01",
//     // status: "online",
//   },
//   {
//     id: 2,
//     name: "佐藤花子",
//     department: "デザイン部",
//     // joinDate: "2023-03-15",
//     // status: "offline",
//   },
//   {
//     id: 3,
//     name: "鈴木一郎",
//     department: "営業部",
//     // joinDate: "2023-02-01",
//     // status: "online",
//   },
//   {
//     id: 4,
//     name: "高橋美咲",
//     department: "マーケティング部",
//     // joinDate: "2023-01-10",
//     // status: "away",
//   },
// ]

// export function TeamMemberList() {
//   const router = useRouter()

//   const getStatusColor = (status: string) => {
//     switch (status) {
//       case "online":
//         return "bg-green-500"
//       case "away":
//         return "bg-yellow-500"
//       case "offline":
//         return "bg-gray-400"
//       default:
//         return "bg-gray-400"
//     }
//   }

//   const getStatusText = (status: string) => {
//     switch (status) {
//       case "online":
//         return "オンライン"
//       case "away":
//         return "離席中"
//       case "offline":
//         return "オフライン"
//       default:
//         return "不明"
//     }
//   }

