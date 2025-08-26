'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/Table";
import { 
  Search, 
  Building2,
  Eye,
  Users
} from "lucide-react";

interface DepartmentMember {
  id: string;
  user_id: string;
  user?: {
    id: string;
    display_name: string;
    avatar_url?: string;
    profile?: {
      department?: string;
    };
  };
}

interface DepartmentMemberListProps {
  members: DepartmentMember[];
  onViewProfile?: (memberId: string) => void;
}

export default function DepartmentMemberList({
  members,
  onViewProfile
}: DepartmentMemberListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');

  // 部署ごとの色を定義
  const departmentColors = {
    'all': 'bg-gray-500 hover:bg-gray-600',
    'テスト部': 'bg-blue-500 hover:bg-blue-600',
    '企画部': 'bg-green-500 hover:bg-green-600',
    '管理部': 'bg-purple-500 hover:bg-purple-600',
    '開発部': 'bg-orange-500 hover:bg-orange-600',
    '営業部': 'bg-red-500 hover:bg-red-600',
    '人事部': 'bg-pink-500 hover:bg-pink-600',
    '総務部': 'bg-indigo-500 hover:bg-indigo-600',
  };

  // 部署バッジの色を定義
  const departmentBadgeColors = {
    'テスト部': 'border-blue-500 text-blue-700 bg-blue-50',
    '企画部': 'border-green-500 text-green-700 bg-green-50',
    '管理部': 'border-purple-500 text-purple-700 bg-purple-50',
    '開発部': 'border-orange-500 text-orange-700 bg-orange-50',
    '営業部': 'border-red-500 text-red-700 bg-red-50',
    '人事部': 'border-pink-500 text-pink-700 bg-pink-50',
    '総務部': 'border-indigo-500 text-indigo-700 bg-indigo-50',
  };
  
  // 部署の一覧を取得（正規化して重複を除去）
  const normalizeDepartment = (dept: string | undefined) => dept?.trim() || '';
  
  const departments = ['all', ...Array.from(new Set(
    members
      .map(m => m.user?.profile?.department)
      .filter(Boolean)
      .map(normalizeDepartment)
  )).sort()]; // 部署をあいうえお順でソート
  
  // デバッグ用：部署の重複を確認
  console.log('部署一覧:', departments);
  console.log('メンバーの部署:', members.map(m => m.user?.profile?.department).filter(Boolean));
  
  // 部署別のメンバー数を計算
  const departmentCounts = departments.reduce((acc, dept) => {
    if (dept === 'all') {
      acc[dept] = members.length;
    } else if (dept) {
      acc[dept] = members.filter(m => 
        normalizeDepartment(m.user?.profile?.department || '') === dept
      ).length;
    }
    return acc;
  }, {} as Record<string, number>);

  // 検索とフィルタリング
  const filteredMembers = members.filter(member => {
    if (!member.user) return false;
    
    const displayName = member.user.display_name || '';
    const userId = member.user.id || '';
    const matchesSearch = displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         userId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = selectedDepartment === 'all' || 
                             normalizeDepartment(member.user.profile?.department || '') === selectedDepartment;
    
    return matchesSearch && matchesDepartment;
  }).sort((a, b) => {
    // 部署順でソート（部署が同じ場合は名前順）
    const deptA = normalizeDepartment(a.user?.profile?.department || '');
    const deptB = normalizeDepartment(b.user?.profile?.department || '');
    const nameA = a.user?.display_name || '';
    const nameB = b.user?.display_name || '';
    
    if (deptA !== deptB) {
      return deptA.localeCompare(deptB, 'ja'); // 部署をあいうえお順でソート
    }
    return nameA.localeCompare(nameB, 'ja'); // 部署が同じ場合は名前をあいうえお順でソート
  });

  return (
    <Card className="w-full">
      <CardContent>
        {/* 部署選択 */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3 justify-center">
            {departments.map((dept) => {
              const isSelected = selectedDepartment === dept;
              const normalizedDept = normalizeDepartment(dept);
              const colorClass = departmentColors[normalizedDept as keyof typeof departmentColors] || 'bg-gray-500 hover:bg-gray-600';
              
              return (
                <Button
                  key={dept}
                  variant={isSelected ? "default" : "outline"}
                  size="sm"
                  onClick={() => dept && setSelectedDepartment(dept)}
                  className={`flex items-center gap-2 px-4 py-2 ${
                    isSelected 
                      ? `${colorClass} text-white border-0` 
                      : 'hover:bg-gray-100 border-gray-300'
                  }`}
                >
                  <Users className="h-4 w-4" />
                  {dept === 'all' ? '全部署' : dept}
                  <Badge variant={isSelected ? "secondary" : "outline"} className="ml-1">
                    {dept ? departmentCounts[dept] : 0}
                  </Badge>
                </Button>
              );
            })}
          </div>
        </div>

        {/* 検索 */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="メンバーを検索..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* メンバー一覧 */}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>名前</TableHead>
                <TableHead>部署</TableHead>
                <TableHead className="text-center">プロフィール</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredMembers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-gray-500 py-8">
                    メンバーが見つかりません
                  </TableCell>
                </TableRow>
              ) : (
                filteredMembers.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={member.user?.avatar_url} alt={member.user?.display_name || ''} />
                          <AvatarFallback>
                            {(member.user?.display_name || '?').charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div className="font-medium">
                          {member.user?.display_name?.startsWith('admin@') 
                            ? '管理者1' 
                            : member.user?.display_name || '不明'}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={
                          member.user?.profile?.department 
                            ? departmentBadgeColors[normalizeDepartment(member.user.profile.department) as keyof typeof departmentBadgeColors] || 'border-gray-300'
                            : 'border-gray-300'
                        }
                      >
                        {member.user?.profile?.department || '未設定'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex flex-col items-center gap-2">
                        {onViewProfile && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onViewProfile(member.id)}
                            className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300 transition-colors"
                          >
                            <Eye className="h-4 w-4" />
                            詳細
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
