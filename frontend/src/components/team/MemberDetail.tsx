"use client";

import { useEffect, useState, Fragment  } from "react";
import { getMemberProfile } from "@/lib/api/teamMembers";
import type { MemberProfile } from "@/lib/api/teamMembers";
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
  Brain,
  TrendingUp,
  Lightbulb,
} from "lucide-react";

type Props = { memberId: string };

export function MemberDetail({ memberId }: Props) {
  const [data, setData] = useState<MemberProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        // プレゼンテーション用：モックデータからメンバー詳細を取得
        const profile = await getMemberProfile(memberId);
        setData(profile);
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

  const p: MemberProfile = data;

  // value のフォーマット（空なら "未設定"）
  const v = (x: any) => (x && String(x).trim() ? String(x) : "未設定");

  const fields: { icon: JSX.Element; label: string; value: string }[] = [
    { icon: <UserIcon className="h-4 w-4" />, label: "名前", value: v(data.display_name) },
    { icon: <Briefcase className="h-4 w-4" />, label: "部署", value: v(p.department) },
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

  // AI分析フィードバックのモックデータ
  const aiAnalysisFeedback = [
    {
      icon: <Brain className="h-5 w-5 text-blue-600" />,
      title: "話題提供",
      content: "家電量販店からの転職であり、過去に月間売上日本一に輝いた経歴あり",
      score: "A+",
      category: "コミュニケーション"
    },
    {
      icon: <TrendingUp className="h-5 w-5 text-green-600" />,
      title: "成長性・学習意欲",
      content: "新しい技術への関心が高く、自己学習を継続的に行っています。チームメンバーからのフィードバックを積極的に受け入れ、改善に活かす姿勢が見られます。",
      score: "A",
      category: "成長性"
    },
    {
      icon: <Lightbulb className="h-5 w-5 text-purple-600" />,
      title: "問題解決能力",
      content: "複雑な課題に対して論理的にアプローチし、効率的な解決策を提案できます。チーム全体の視点で物事を考えることができ、長期的な改善案も提示しています。",
      score: "A-",
      category: "問題解決"
    }
  ];

  return (
    <div className="mx-auto max-w-2xl rounded-2xl bg-white shadow p-6 border space-y-6">
      {/* ヘッダー（アイコン・名前・部署・メール） */}
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
        <div className="flex-1">
          <div className="text-lg font-bold text-gray-900">{data.display_name}</div>
          <div className="text-sm text-gray-600">{data.email}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {p.department ?? "部署未設定"}
            </span>
            <span className="text-xs text-gray-500">
              入社: {p.join_date ? new Date(p.join_date).toLocaleDateString('ja-JP') : "未設定"}
            </span>
          </div>
        </div>
      </div>

      {/* 詳細一覧 */}
      <section>
        <ul className="divide-y">
          {fields.slice(4).map((f, i) => ( // 名前、部署、入社日、生年月日は既にヘッダーに表示済み
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

      {/* AI分析フィードバック */}
      <section className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Brain className="h-5 w-5 text-blue-600" />
          AI分析フィードバック
        </h3>
        <div className="space-y-4">
          {aiAnalysisFeedback.map((feedback, index) => (
            <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {feedback.icon}
                  <h4 className="font-medium text-gray-900">{feedback.title}</h4>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-600 text-white">
                  {feedback.score}
                </span>
              </div>
              <p className="text-sm text-gray-700 mb-2">{feedback.content}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-600 font-medium">{feedback.category}</span>
                <span className="text-xs text-gray-500">AI分析結果</span>
              </div>
            </div>
          ))}
        </div>
      </section>
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
