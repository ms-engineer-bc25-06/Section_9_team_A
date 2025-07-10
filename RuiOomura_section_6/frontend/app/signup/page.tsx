// SignUp page
"use client";

import React from 'react';
import { useState } from 'react';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
console.log(auth);

export default function SignUpPage() {
    const [email, setEmail] = useState(""); // メールアドレスの状態
    const [password, setPassword] = useState(""); // パスワードの状態
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault(); // ページのリロードを防ぐ
        console.log("メール:", email);
        console.log("パスワード", password);

        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            console.log("ユーザー登録成功:", userCredential.user);
        } catch(error) {
            console.error("ユーザー登録失敗:", error);
        };
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



// TODO: block7エラーハンドリングとバリデーション
/*
    メールアドレスが空でないか？
    パスワードが空でないか？
    パスワードが6文字以上か？

    バリデーションに引っかかった場合はcreate～()を実行しない
*/
// TODO: エラーメッセージを画面表示
/*
    ・errorMessageという状態変数をuseStateで定義
    ・バリデーション or Firebaseのエラーが発生したらメッセージを入れる
    ・JSX内に{errorMessage && <p>{errorMessage}</p>}のように表示する
*/

// TODO:サインアップ後の画面遷移

