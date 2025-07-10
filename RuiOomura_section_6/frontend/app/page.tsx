// Top Page
"use client";

import React from 'react';
import Link from 'next/link';
import { onAuthStateChanged, signOut, User } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { useEffect, useState } from 'react';

export default function Home() {
    // Firebase Authでログイン状態（認証状態）を検出できるようにする
    const [user, setUser] = useState<User | null>(null);

const handleLogout = async () => {
    try {
        await signOut(auth);
        // 成功時の処理
        console.log("ログアウトに成功しました");
        setUser(null); // 状態も更新
    } catch (error) {
        // エラー時の処理
        console.error('ログアウトエラー', error);
    };


};
// 現在のログインユーザーを取得、状態が変わるたびにuserを更新
useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
        setUser(currentUser);
    });

    return () => unsubscribe();
}, []);

    return (
        <main>
            {/* ヘッダー */}
            <header>
                <h1>ごきげんよう</h1>
            </header>
           
            {/* 画像エリア */}
            <section>
                <img src="noimage.png" alt="top_image" />
            </section>

            {/* プロフィールテキスト */}
            <section>
                <h2>profile</h2>
                <p>profile_text</p>
            </section>   

            {/* サインアップボタン・サインインボタン */}
            <section>
                {user ? (
                    <>
                        <p>ごきげんよう {user.email} さん</p>
                        <button onClick={async () => await signOut(auth)}>sign out</button>
                    </>
                ) : (
                    <>
                        <Link href="/signin">
                            <button>sign in</button>
                        </Link>
                        <Link href="/signup">
                            <button>sign up</button>
                        </Link>
                    </>
                )}
            </section>

            {/* インスタ風エリア */}
            <section>
                <h3>DATEstagram</h3>
                <ul>
                    <li>
                        <img src="noimage.png" alt="No.1" />
                        <p>No.1</p>
                    </li>
                    <li>
                        <img src="noimage.png" alt="No.2" />
                        <p>No.2</p>
                    </li>
                </ul>
            </section>
        </main>
    );
};

// PostgreSQL + Prisma + DockerによるDB接続の準備
/*
    目的：
        ・DockerでPostgreSQLコンテナを立ち上げてローカル開発用DBを用意
        ・Prismaを使ってデータベーススキーマを定義し、マイグレーションテーブルを作成
        ・今後Express.js側からデータを読み書きできる基盤を整える
    
    手順；
    1.DockerでPostgreSQLのコンテナを立ち上げる
        ・Dockerを使ってPostgreSQL_DBを仮想的に立ち上げる
    2.PostgreSQLが起動していることを確認
    3.Prismaをインストールし、初期設定する
    4.Prismaスキーマ（DBモデル）を定義する
    5.Prismaマイグレーションを実行
    6.Prisma Clientを生成して使えるようにする
*/