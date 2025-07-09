// Sign Up Page
import { initializeApp } from 'firebase/app';
import { getAuth, createUserWithEmailAndPassword } from 'firebase/auth';

// 新規ユーザーがメールアドレスとパスワードを使用してアプリに登録できるフォームを作成
const app = initializeApp(firebaseConfig);
const auth = getAuth();
createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
        // Signed up
        const user = userCredential.user;

    }).catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
    })





