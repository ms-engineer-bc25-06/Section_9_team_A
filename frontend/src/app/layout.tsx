"use client"
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from '@/lib/theme';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
