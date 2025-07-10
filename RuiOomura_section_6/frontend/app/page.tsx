// Top Page
"use client";

import React from 'react';
import Link from 'next/link';

export default function Home() {
    return (
        <main>
            {/* ヘッダー */}
            <header>
                <h1>ごきげんよう</h1>
            </header>
           
            {/* 画像エリア */}
            <section>
                <img src="" alt="top_image" />
            </section>

            {/* プロフィールテキスト */}
            <section>
                <h2>profile</h2>
                <p>profile_text</p>
            </section>   

            {/* サインアップボタン・サインインボタン */}
            <section>
                <Link href="/signin">
                    <button>sign in</button>
                </Link>

                <Link href="/signup">
                    <button>sign up</button>
                </Link>
            </section>
            
            {/* インスタ風エリア */}
            <section>
                <h3>DATEstagram</h3>
                <ul>
                    <li>
                        <img src="" alt="No.1" />
                        <p>No.1</p>
                    </li>
                    <li>
                        <img src="" alt="No.2" />
                        <p>No.2</p>
                    </li>
                </ul>
            </section>
        </main>
    );
};
