'use client';

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Stack,
} from '@mui/material';
import {
  Mic,
  Analytics,
  Group,
  Security,
  Speed,
  Support,
} from '@mui/icons-material';

export default function HomePage() {
  return (
    <Box sx={{ minHeight: '100vh' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 8,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" gutterBottom>
                Bridge Line
              </Typography>
              <Typography variant="h5" component="h2" gutterBottom>
                AI音声チャットで新しいコミュニケーションを
              </Typography>
              <Typography variant="body1" sx={{ mb: 4, opacity: 0.9 }}>
                リアルタイム音声チャットとAI分析を組み合わせた、
                次世代のコミュニケーションプラットフォーム
              </Typography>
              <Stack direction="row" spacing={2}>
                <Button
                  variant="contained"
                  size="large"
                  sx={{ bgcolor: 'white', color: 'primary.main' }}
                >
                  無料で始める
                </Button>
                <Button variant="outlined" size="large" sx={{ color: 'white', borderColor: 'white' }}>
                  詳細を見る
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  width: '100%',
                  height: 400,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="h6" sx={{ opacity: 0.7 }}>
                  音声チャットデモ
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
          主な機能
        </Typography>
        <Typography variant="body1" textAlign="center" sx={{ mb: 6, color: 'text.secondary' }}>
          Bridge Lineが提供する革新的な機能をご紹介します
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Mic sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" component="h3" gutterBottom>
                  リアルタイム音声チャット
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  高品質な音声通話とリアルタイム文字起こしで、
                  効率的なコミュニケーションを実現します。
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Analytics sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" component="h3" gutterBottom>
                  AI分析
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  会話の感情分析、参加度分析、性格洞察など、
                  AIによる詳細な分析結果を提供します。
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Group sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" component="h3" gutterBottom>
                  チーム管理
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  チーム作成、メンバー招待、権限管理など、
                  組織での利用に最適な機能を提供します。
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Benefits Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
            なぜBridge Lineなのか
          </Typography>
          <Grid container spacing={4} sx={{ mt: 4 }}>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Security sx={{ fontSize: 30, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6">セキュリティ重視</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                エンドツーエンド暗号化とFirebase認証により、
                安全で信頼性の高いサービスを提供します。
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Speed sx={{ fontSize: 30, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6">高速・低遅延</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                WebRTC技術により、高品質で低遅延な
                音声通話を実現します。
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Analytics sx={{ fontSize: 30, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6">AI分析</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                OpenAI技術を活用した高度な分析により、
                コミュニケーションの質を向上させます。
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Support sx={{ fontSize: 30, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6">24/7サポート</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                専門チームによる24時間体制のサポートで、
                安心してご利用いただけます。
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h3" component="h2" gutterBottom>
          今すぐ始めましょう
        </Typography>
        <Typography variant="body1" sx={{ mb: 4, color: 'text.secondary' }}>
          無料プランでBridge Lineの機能をお試しください
        </Typography>
        <Button variant="contained" size="large">
          無料アカウント作成
        </Button>
      </Container>
    </Box>
  );
}
