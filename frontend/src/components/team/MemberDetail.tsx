"use client";

import { useEffect, useState, Fragment  } from "react";
import { apiGet } from "@/lib/apiClient";
import type { UserDetailResponse, MemberProfile } from "@/types/team";
import {
  User as UserIcon,
  Briefcase,
  CalendarDays,
  Cake,
  MapPin,
  Home,
  Heart,
  Trophy,
  Sun,
  Utensils,
  BookOpen,
  Music,
  PawPrint,
  Star,
  Quote,
  Target,
  MessageSquare,
} from "lucide-react";

type Props = { memberId: string };

export function MemberDetail({ memberId }: Props) {
  const [data, setData] = useState<UserDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiGet<UserDetailResponse>(`/users/${memberId}`);
        setData(res);
      } catch (e: any) {
        setErr(e?.message ?? "メンバー詳細の取得に失敗しました。");
      } finally {
        setLoading(false);
      }
    })();
  }, [memberId]);

  if (loading) return <div className="text-sm text-gray-600">読み込み中…</div>;
  if (err) return <div className="text-sm text-red-600">{err}</div>;
  if (!data) return null;

  const p: MemberProfile = data.profile ?? {};

  // value のフォーマット（空なら "未設定"）
  const v = (x: any) => (x && String(x).trim() ? String(x) : "未設定");

  const fields: { icon: JSX.Element; label: string; value: string }[] = [
    { icon: <UserIcon className="h-4 w-4" />, label: "名前", value: v(data.display_name) },
    { icon: <Briefcase className="h-4 w-4" />, label: "部署", value: v(p.department) },
    { icon: <UserIcon className="h-4 w-4" />, label: "ニックネーム", value: v(p.nickname) },
    { icon: <CalendarDays className="h-4 w-4" />, label: "入社年月", value: v(p.join_date) },
    { icon: <Cake className="h-4 w-4" />, label: "生年月日", value: v(p.birth_date) },
    { icon: <MapPin className="h-4 w-4" />, label: "出身地", value: v(p.hometown) },
    { icon: <Home className="h-4 w-4" />, label: "居住地", value: v(p.residence) },
    { icon: <Heart className="h-4 w-4" />, label: "趣味／特技", value: v(p.hobbies) },
    { icon: <Trophy className="h-4 w-4" />, label: "学生時代の部活／サークル", value: v(p.student_activities) },
    { icon: <Sun className="h-4 w-4" />, label: "休日の過ごし方", value: v(p.holiday_activities) },
    { icon: <Utensils className="h-4 w-4" />, label: "好きな食べ物", value: v(p.favorite_food) },
    { icon: <BookOpen className="h-4 w-4" />, label: "好きな本・漫画・映画・ドラマ", value: v(p.favorite_media) },
    { icon: <Music className="h-4 w-4" />, label: "好きな音楽・カラオケの18番", value: v(p.favorite_music) },
    { icon: <PawPrint className="h-4 w-4" />, label: "ペット・推し", value: v(p.pets_oshi) },
    { icon: <Star className="h-4 w-4" />, label: "尊敬する人", value: v(p.respected_person) },
    { icon: <Quote className="h-4 w-4" />, label: "座右の銘", value: v(p.motto) },
    { icon: <Target className="h-4 w-4" />, label: "将来の目標・生きてるうちにやってみたいこと", value: v(p.future_goals) },
  ];


  return (
    <div className="mx-auto max-w-2xl rounded-2xl bg-white shadow p-6 border space-y-6">
      {/* ヘッダー（アイコン・名前・部署） */}
      <div className="flex items-center gap-3">
        {data.avatar_url ? (
          <img
            src={data.avatar_url}
            alt={`${data.display_name}のアイコン`}
            className="h-12 w-12 rounded-full object-cover border"
          />
        ) : (
          <div className="h-12 w-12 rounded-full border grid place-items-center text-base text-gray-600 bg-gray-50">
            {(data.display_name || "？").slice(0, 1)}
          </div>
        )}
        <div>
          <div className="text-lg font-bold text-gray-900">{data.display_name}</div>
          <div className="text-sm text-gray-600">{p.department ?? "部署未設定"}</div>
        </div>
      </div>

      {/* 詳細一覧 */}
      <section>
        <ul className="divide-y">
          {fields.map((f, i) => (
            <li key={i} className="py-3 flex items-start gap-3">
              <span className="mt-1">{f.icon}</span>
              <div className="min-w-0">
                <div className="text-xs text-gray-500">{f.label}</div>
                <div className="text-sm text-gray-900 break-words">{f.value}</div>
              </div>
            </li>
          ))}
        </ul>
      </section>

             {/* フィードバック一覧 */}
       {p.feedback && p.feedback.length > 0 ? (
        <section className="border-t pt-6">
                     <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
             <MessageSquare className="h-5 w-5 text-green-600" />
             フィードバック一覧
           </h3>
          
          {/* フィードバック一覧 */}
          {p.feedback && p.feedback.length > 0 && (
            <div className="mb-6">
              <h4 className="text-md font-medium text-gray-800 mb-3 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-green-600" />
                フィードバック一覧
              </h4>
              <div className="space-y-3">
                {p.feedback.map((feedback, index) => (
                  <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <p className="text-sm text-green-800">{feedback}</p>
                  </div>
                ))}
              </div>
            </div>
          )}


        </section>
      ) : (
                 <section className="border-t pt-6">
           <div className="text-center text-gray-500 py-8">
             <MessageSquare className="h-12 w-12 mx-auto text-gray-300 mb-3" />
             <p className="text-sm">フィードバックはまだありません</p>
             <p className="text-xs text-gray-400 mt-1">マイプロフィールでフィードバックを登録すると表示されます</p>
           </div>
         </section>
      )}
    </div>
  );
}


//// mockデータ
// interface Props {
//   memberId: string
// }

// const mockMemberDetail = {
//   id: 1,
//   name: "田中太郎",
//   department: "開発部",
//   nickname: "太郎",
//   join_date: "2023-04-01",
//   birth_date: "1990-05-15",
//   hometown: "東京都",
//   residence: "神奈川県横浜市",
//   hobbies: "プログラミング、読書、映画鑑賞",
//   student_activities: "テニス部",
//   holiday_activities: "カフェ巡り、散歩",
//   favorite_food: "ラーメン、寿司",
//   favorite_media: "映画、漫画、ドラマ",
//   favorite_music: "カラオケの18番",
//   pets_oshi: "犬、猫",
//   respected_person: "父親",
//   motto: "努力は報われる",
//   future_goals: "エンジニアとしての成長",
//   feedback: [
//     "いつも丁寧に教えてくれてありがとうございます！",
//     "チームワークを大切にしてくれる素晴らしい方です",
//     "技術力が高く、頼りになる存在です",
//   ],
// }

// export function MemberDetail({ memberId }: Props) {
//   const member = mockMemberDetail // 実際はAPIから取得

//   const profileItems = [
//     { icon: User, label: "名前", value: member.name },
//     { icon: Briefcase, label: "部署", value: member.department },
//     { icon: User, label: "ニックネーム", value: member.nickname },
//     { icon: CalendarDays, label: "入社年月", value: member.join_date },
//     { icon: Cake, label: "生年月日", value: member.birth_date },
//     { icon: MapPin, label: "出身地", value: member.hometown },
//     { icon: Home, label: "居住地", value: member.residence },
//     { icon: Heart, label: "趣味／特技", value: member.hobbies },
//     { icon: Trophy, label: "学生時代の部活／サークル", value: member.student_activities },
//     { icon: Sun, label: "休日の過ごし方", value: member.holiday_activities },
//     { icon: Utensils, label: "好きな食べ物", value: member.favorite_food },
//     { icon: BookOpen, label: "好きな本・漫画・映画・ドラマ", value: member.favorite_media },
//     { icon: Music, label: "好きな音楽・カラオケの18番", value: member.favorite_music },
//     { icon: PawPrint, label: "ペット・推し", value: member.pets_oshi },
//     { icon: Star, label: "尊敬する人", value: member.respected_person },
//     { icon: Quote, label: "座右の銘", value: member.motto },
//     { icon: Target, label: "将来の目標・生きてるうちにやってみたいこと ", value: member.future_goals },
//   ]
