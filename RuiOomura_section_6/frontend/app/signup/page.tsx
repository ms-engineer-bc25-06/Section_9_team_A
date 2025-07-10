// SignUp page
"use client";

import React from 'react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { FirebaseError } from 'firebase/app';
import { auth } from '@/lib/firebase';
import { getFirebaseErrorMessage } from '@/lib/firebaseError';

type FormData = {
    email: string;
    password: string;
};

export default function SignUpPage() {
    const router = useRouter();
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
    const onSubmit = async (data: FormData) => {
        // TODO: console.log消す
        console.log("メール:", data.email);
        console.log("パスワード", data.password);

        // サーバーに送信する処理
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, data.email, data.password);
            // TODO: console.log消す
            console.log("ユーザー登録成功:", userCredential.user);
            setErrorMessage(null);
            router.push('/'); // topページへ
        } catch(error) {
            // TODO: console.log消す
            console.error("ユーザー登録失敗:", error);
            if (error instanceof FirebaseError) {
                const message = getFirebaseErrorMessage(error.code);
                setErrorMessage(message);
            } else {
                setErrorMessage('予期しないエラーが発生しました');
            };
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

            {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
            {errorMessage && <p className="text-red-600 text-sm">{errorMessage}</p>}

            <button type="submit" className="bg-blue-500 text-white p-2 rounded">
                Sign Up
            </button>  
        </form>
    );
};


// TODO:サインアップ後の画面遷移
/*

*/
