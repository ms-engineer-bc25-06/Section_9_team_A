'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Alert, AlertDescription } from "@/components/ui/Alert";
import { CreditCard, Users, ArrowRight, CheckCircle } from "lucide-react";

export default function BillingPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">決済・課金管理</h1>
          <p className="text-gray-600">
            組織の利用状況と課金情報を確認できます
          </p>
        </div>

        {/* 現在の利用状況 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              現在の利用状況
            </CardTitle>
            <CardDescription>
              組織のメンバー数と課金状況
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">10</div>
                <div className="text-sm text-gray-600">無料枠</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">8</div>
                <div className="text-sm text-gray-600">現在のメンバー</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">2</div>
                <div className="text-sm text-gray-600">残り枠</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 課金プラン */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              課金プラン
            </CardTitle>
            <CardDescription>
              現在のプランと料金体系
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>基本プラン</span>
                <span className="font-medium">無料</span>
              </div>
              <div className="flex justify-between items-center">
                <span>含まれる機能</span>
                <span className="text-sm text-gray-600">基本的な機能（10人まで）</span>
              </div>
              <div className="flex justify-between items-center">
                <span>追加料金</span>
                <span className="text-sm text-gray-600">1人あたり¥500/月</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* アクション */}
        <div className="text-center space-y-4">
          <Alert className="max-w-md mx-auto">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              現在のメンバー数は無料枠内です。追加の決済は不要です。
            </AlertDescription>
          </Alert>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard">
              <Button variant="outline">
                ダッシュボードに戻る
              </Button>
            </Link>
            
            <Link href="/billing/subscription">
              <Button className="bg-blue-600 hover:bg-blue-700">
                ユーザー枠を追加
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
