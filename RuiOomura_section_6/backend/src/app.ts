import express from 'express';
import cors from 'cors';
import userRouter from './router/user';
import topImageRouter from "./router/topImage";

const app = express();
const port = 4000;

// リクエストボディをJSONとして扱うミドルウェア
app.use(express.json());
app.use(cors());

// Routerのミドルウェア
app.use('/user', userRouter);
app.use('/topImage', topImageRouter);


// エンドポイント（最終処理）
app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});