// SignUp page
"use client";

import React from 'react';
import { useState } from 'react';
import { auth } from '@/lib/firebase';
console.log(auth);

export default function SignUpPage() {
    const [email, setEmail] = useState(""); // メールアドレスの状態
    const [password, setPassword] = useState(""); // パスワードの状態
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault(); // ページのリロードを防ぐ
        console.log("メール:", email);
        console.log("パスワード", password);
        // TODO:firebase処理を書く
        // TODO:Firebase Authでサインアップするロジックの実装
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-md mx-auto mt-20">
            <input
                type="email"
                placeholder="email@abc.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="p-2 border rounded"     
            />
            <input
                type="password"
                placeholder="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="p-2 border rounded"
            />
            <button type="submit" className="bg-blue-500 text-white p-2 rounded">
                Sign Up
            </button>  
        </form>
    );
};



// TODO:エラーハンドリングとバリデーション
// TODO:サインアップ後の画面遷移

