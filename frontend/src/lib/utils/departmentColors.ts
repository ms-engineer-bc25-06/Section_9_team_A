// 部署ごとの色を取得するユーティリティ関数

export const getDepartmentColor = (departmentName: string): string => {
  const colors: Record<string, string> = {
    '企画部': 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100',
    '開発部': 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100',
    '営業部': 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100',
    '人事部': 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100',
    '経理部': 'bg-pink-50 text-pink-700 border-pink-200 hover:bg-pink-100',
    '管理部': 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100',
    'テスト部': 'bg-cyan-50 text-cyan-700 border-cyan-200 hover:bg-cyan-100',
    'マーケティング部': 'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100',
    'カスタマーサポート部': 'bg-teal-50 text-teal-700 border-teal-200 hover:bg-teal-100',
    '法務部': 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100',
  };

  return colors[departmentName] || 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100';
};
