'use client';

import React, { useState } from 'react';
import { TeamDynamicsDashboard } from '@/components/team-dynamics';

export default function TeamDynamicsPage() {
  const [selectedTeamId, setSelectedTeamId] = useState<number>(1); // デフォルトでチームID 1
  const [selectedSessionId, setSelectedSessionId] = useState<number | undefined>();

  return (
    <div className="container mx-auto py-6 px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">チームダイナミクス分析</h1>
        <p className="text-gray-600">チームの相互作用、相性、結束力を分析します</p>
      </div>

      {/* チーム選択 */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          チームID
        </label>
        <input
          type="number"
          value={selectedTeamId}
          onChange={(e) => setSelectedTeamId(parseInt(e.target.value) || 1)}
          className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          min="1"
        />
        
        <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
          セッションID (オプション)
        </label>
        <input
          type="number"
          value={selectedSessionId || ''}
          onChange={(e) => setSelectedSessionId(e.target.value ? parseInt(e.target.value) : undefined)}
          className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="任意"
        />
      </div>

      {/* チームダイナミクスダッシュボード */}
      <TeamDynamicsDashboard 
        teamId={selectedTeamId} 
        sessionId={selectedSessionId} 
      />
    </div>
  );
}
