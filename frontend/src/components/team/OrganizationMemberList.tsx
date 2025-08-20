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
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/DropdownMenu";
import { 
  Search, 
  Filter, 
  MoreHorizontal, 
  UserPlus, 
  Settings, 
  Trash2,
  Eye,
  Edit,
  Crown
} from "lucide-react";

interface OrganizationMember {
  id: string;
  user_id: string;
  organization_id: string;
  role: string;
  status: string;
  joined_at: string;
  user: {
    display_name: string;
    email: string;
    avatar_url?: string;
  };
}

interface OrganizationMemberListProps {
  members: OrganizationMember[];
  onAddMember?: () => void;
  onEditMember?: (memberId: string) => void;
  onRemoveMember?: (memberId: string) => void;
  onViewProfile?: (memberId: string) => void;
  currentUserRole?: string;
}

export default function OrganizationMemberList({
  members,
  onAddMember,
  onEditMember,
  onRemoveMember,
  onViewProfile,
  currentUserRole = 'member'
}: OrganizationMemberListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // 検索とフィルタリング
  const filteredMembers = members.filter(member => {
    const matchesSearch = member.user.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         member.user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || member.role === filterRole;
    const matchesStatus = filterStatus === 'all' || member.status === filterStatus;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'owner':
        return 'default';
      case 'admin':
        return 'secondary';
      case 'moderator':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'pending':
        return 'outline';
      case 'suspended':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const canManageMembers = currentUserRole === 'owner' || currentUserRole === 'admin';

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <UserPlus className="h-5 w-5" />
              組織メンバー ({filteredMembers.length}人)
            </CardTitle>
            <CardDescription>
              組織に所属するメンバーの一覧と管理
            </CardDescription>
          </div>
          {canManageMembers && onAddMember && (
            <Button onClick={onAddMember}>
              <UserPlus className="h-4 w-4 mr-2" />
              メンバーを追加
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* 検索とフィルター */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
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
          
          <div className="flex gap-2">
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">全役割</option>
              <option value="owner">オーナー</option>
              <option value="admin">管理者</option>
              <option value="moderator">モデレーター</option>
              <option value="member">メンバー</option>
            </select>
            
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">全ステータス</option>
              <option value="active">アクティブ</option>
              <option value="pending">保留中</option>
              <option value="suspended">停止中</option>
            </select>
          </div>
        </div>

        {/* メンバー一覧 */}
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>メンバー</TableHead>
                <TableHead>役割</TableHead>
                <TableHead>ステータス</TableHead>
                <TableHead>参加日</TableHead>
                <TableHead className="text-right">アクション</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredMembers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-gray-500 py-8">
                    メンバーが見つかりません
                  </TableCell>
                </TableRow>
              ) : (
                filteredMembers.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={member.user.avatar_url} alt={member.user.display_name} />
                          <AvatarFallback>
                            {member.user.display_name.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium flex items-center gap-2">
                            {member.user.display_name}
                            {member.role === 'owner' && (
                              <Crown className="h-4 w-4 text-yellow-500" />
                            )}
                          </div>
                          <div className="text-sm text-gray-500">{member.user.email}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(member.role)}>
                        {member.role === 'owner' && 'オーナー'}
                        {member.role === 'admin' && '管理者'}
                        {member.role === 'moderator' && 'モデレーター'}
                        {member.role === 'member' && 'メンバー'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusBadgeVariant(member.status)}>
                        {member.status === 'active' && 'アクティブ'}
                        {member.status === 'pending' && '保留中'}
                        {member.status === 'suspended' && '停止中'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-gray-500">
                        {new Date(member.joined_at).toLocaleDateString('ja-JP')}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {onViewProfile && (
                            <DropdownMenuItem onClick={() => onViewProfile(member.id)}>
                              <Eye className="h-4 w-4 mr-2" />
                              プロフィール表示
                            </DropdownMenuItem>
                          )}
                          
                          {canManageMembers && onEditMember && (
                            <DropdownMenuItem onClick={() => onEditMember(member.id)}>
                              <Edit className="h-4 w-4 mr-2" />
                              編集
                            </DropdownMenuItem>
                          )}
                          
                          {canManageMembers && onRemoveMember && member.role !== 'owner' && (
                            <DropdownMenuItem 
                              onClick={() => onRemoveMember(member.id)}
                              className="text-red-600"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              削除
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
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
