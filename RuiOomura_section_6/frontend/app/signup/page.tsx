// SignUp page
// NOTE: App Routerでは状態管理を行うときに必ず書く
"use client" 
// NOTE: これは「このファイルはブラウザ側で動くコードだよ」とNext.jsに伝えるもの

/*
TODO:
    ・メール・パスワードの入力フォーム
    ・Firebase Authを使ってユーザーを新規作成
    ・成功時やエラー時の表示が適切
    ・UIはTailwindCSSを用いる
*/

// TODO:useStateで入力フォームの状態管理（useState）
/*
目的：
    ・「メールアドレス」と「パスワード」を入力できるフォームを作る
    ・「サインアップ」ボタンを作る
    ・見た目はシンプルでよいので、動作重視
準備：
    ・ユーザーが入力したメールとパスワードを保持する「状態」を作る
    →リアルタイムに入力内容を管理できる
    ・具体的に「メール用の状態」と「パスワード用の状態」が必要
*/
import './Form';
import Form from './Form';
function SignUp() {
    return (
        <div>
            <form />
        </div>
    );
}


export default SignUp;




// TODO:Firebase Authでサインアップするロジックの実装


// TODO:エラーハンドリングとバリデーション


// TODO:サインアップ後の画面遷移

