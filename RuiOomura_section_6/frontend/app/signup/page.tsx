// SignUp page
"use client";

import React from 'react';
import { useForm } from 'react-hook-form';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
console.log(auth);

type FormData = {
    email: string;
    password: string;
};

export default function SignUpPage() {
    const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
    const onSubmit = async (data: FormData) => {
        // TODO: console.log消す
        console.log("メール:", data.email);
        console.log("パスワード", data.password);

        // サーバーに送信する処理
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, data.email, data.password);
            console.log("ユーザー登録成功:", userCredential.user);
        } catch(error) {
            console.error("ユーザー登録失敗:", error);
        };
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4 max-w-md mx-auto mt-20">
            <input
                type="email"
                placeholder="email@abc.com"
                {...register('email', { required: "メールアドレスは必須です" })}
                className="p-2 border rounded"     
            />

            {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}

            <input
                type="password"
                placeholder="password"
                {...register('password', { required: "パスワードは必須です", minLength: {
                    value: 6,
                    message: "パスワードは6文字以上にしてください"
                }
             })}
             className="p-2 border rounded"
            />

            {errors.password && <p className="test-red-500 text-sm">{errors.password.message}</p>}

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

