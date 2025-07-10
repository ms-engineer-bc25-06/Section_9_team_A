// error.codeを日本語で返すための設定ページ

export function getFirebaseErrorMessage(code: string): string{
    switch (code) {
        case 'auth/email-already-in-use':
      return 'このメールアドレスはすでに登録されています。';
    case 'auth/invalid-email':
      return 'メールアドレスの形式が正しくありません。';
    case 'auth/weak-password':
      return 'パスワードは6文字以上にしてください。';
    default:
      return 'サインアップに失敗しました。もう一度お試しください。';
    };
};