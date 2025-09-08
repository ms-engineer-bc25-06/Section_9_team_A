'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar";
import { getAvatarUrl } from "@/lib/utils/avatarUtils";
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
  Users,
  User
} from "lucide-react";
import { getDepartmentCounts } from '@/lib/api/teamMembers';
import { getDepartmentColor } from '@/lib/utils/departmentColors';

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
  const [departments, setDepartments] = useState<{name: string, count: number}[]>([]);
  const [loading, setLoading] = useState(true);

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
  }).sort((a, b) => {
    // 五十音順でソート
    const nameA = a.user?.display_name || '';
    const nameB = b.user?.display_name || '';
    return nameA.localeCompare(nameB, 'ja');
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
                className={`flex items-center gap-2 ${
                  selectedDepartment === dept.name 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : getDepartmentColor(dept.name)
                }`}
              >
                <Building2 className="h-4 w-4" />
                {dept.name} ({dept.count})
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
            <div className="space-y-3">
              {filteredMembers.map((member) => (
                <Card 
                  key={member.id} 
                  className="hover:shadow-md transition-shadow"
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      {/* 左側: アバターと名前 */}
                      <div className="flex items-center gap-5 flex-1 mr-8">
                        <Avatar className="h-16 w-16">
                          <AvatarImage 
                            src={getAvatarUrl(member.user?.avatar_url, member.user?.display_name || 'user', 64)} 
                          />
                          <AvatarFallback className="text-xl">
                            {member.user?.display_name?.slice(0, 2) || '??'}
                          </AvatarFallback>
                        </Avatar>
                        <h3 className="font-semibold text-gray-900 text-xl">
                          {member.user?.display_name || '名前未設定'}
                        </h3>
                      </div>
                      
                      {/* 中央: 部署バッジ */}
                      <div className="flex-shrink-0">
                        {member.user?.profile?.department && (
                          <Badge 
                            variant="outline" 
                            className={`text-base px-4 py-2 ${getDepartmentColor(member.user.profile.department)}`}
                          >
                            <Building2 className="h-4 w-4 mr-2" />
                            {member.user.profile.department}
                          </Badge>
                        )}
                      </div>
                      
                      {/* 右側: 詳細ボタン */}
                      <div className="flex-shrink-0 flex-1 flex justify-end ml-8">
                        <Button
                          variant="outline"
                          size="default"
                          className="flex items-center gap-2 text-base px-4 py-2"
                          onClick={() => handleViewProfile(member.id)}
                        >
                          <User className="h-5 w-5" />
                          詳細
                        </Button>
                      </div>
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
