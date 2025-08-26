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
import { getDepartmentCounts } from '@/lib/api/teamMembers';
import { MockDepartment } from '@/data/mockTeamData';

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
  const [departments, setDepartments] = useState<MockDepartment[]>([]);
  const [loading, setLoading] = useState(true);

  // プレゼンテーション用：部署情報を取得
  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        setLoading(true);
        const deptData = await getDepartmentCounts();
        setDepartments(deptData);
      } catch (error) {
        console.error('部署情報の取得に失敗:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDepartments();
  }, []);

  // 検索とフィルタリング
  const filteredMembers = members.filter(member => {
    if (!member.user) return false;
    
    const matchesSearch = searchTerm === '' || 
      member.user.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.user.profile?.department?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = selectedDepartment === 'all' || 
      member.user.profile?.department === selectedDepartment;
    
    return matchesSearch && matchesDepartment;
  });

  const handleViewProfile = (memberId: string) => {
    if (onViewProfile) {
      onViewProfile(memberId);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">部署情報を読み込み中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 検索・フィルター */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            メンバー検索・フィルター
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 検索バー */}
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="名前や部署で検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          {/* 部署フィルター */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedDepartment === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedDepartment('all')}
              className="flex items-center gap-2"
            >
              <Users className="h-4 w-4" />
              全員 ({members.length})
            </Button>
            
            {departments.map((dept) => (
              <Button
                key={dept.name}
                variant={selectedDepartment === dept.name ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedDepartment(dept.name)}
                className={`flex items-center gap-2 ${dept.name === 'all' ? '' : dept.color}`}
              >
                <Building2 className="h-4 w-4" />
                {dept.name} ({dept.memberCount})
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* メンバー一覧 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            メンバー一覧 ({filteredMembers.length}人)
          </CardTitle>
          <CardDescription>
            検索結果: {searchTerm ? `"${searchTerm}"` : '全員'} 
            {selectedDepartment !== 'all' && ` / ${selectedDepartment}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredMembers.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>条件に一致するメンバーが見つかりません</p>
              <p className="text-sm mt-1">検索条件やフィルターを変更してみてください</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredMembers.map((member) => (
                <Card 
                  key={member.id} 
                  className="hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => handleViewProfile(member.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      {/* アバター */}
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={member.user?.avatar_url} />
                        <AvatarFallback className="text-lg">
                          {member.user?.display_name?.slice(0, 2) || '??'}
                        </AvatarFallback>
                      </Avatar>
                      
                      {/* メンバー情報 */}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {member.user?.display_name || '名前未設定'}
                        </h3>
                        {member.user?.profile?.department && (
                          <Badge variant="outline" className="text-xs mt-1">
                            {member.user.profile.department}
                          </Badge>
                        )}
                      </div>
                      
                      {/* 詳細ボタン */}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="shrink-0"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleViewProfile(member.id);
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
