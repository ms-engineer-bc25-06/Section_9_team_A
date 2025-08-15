module.exports = {
  // 行の長さ
  printWidth: 80,
  
  // タブ幅
  tabWidth: 2,
  
  // タブの使用
  useTabs: false,
  
  // セミコロンの使用
  semi: true,
  
  // シングルクォートの使用
  singleQuote: true,
  
  // オブジェクトの括弧内のスペース
  bracketSpacing: true,
  
  // JSXの括弧内のスペース
  bracketSameLine: false,
  
  // アロー関数の括弧
  arrowParens: 'avoid',
  
  // 末尾のカンマ
  trailingComma: 'es5',
  
  // ファイル末尾の改行
  endOfLine: 'lf',
  
  // インポートの整理
  importOrder: [
    '^react$',
    '^next(.*)$',
    '^@/(.*)$',
    '^[./]',
  ],
  
  // インポートの区切り
  importOrderSeparation: true,
  
  // インポートの並び替え
  importOrderSortSpecifiers: true,
  
  // JSXの改行
  jsxSingleQuote: false,
  
  // プロパティのクォート
  quoteProps: 'as-needed',
  
  // プロセッサー
  overrides: [
    {
      files: '*.{ts,tsx}',
      options: {
        parser: 'typescript',
      },
    },
    {
      files: '*.{js,jsx}',
      options: {
        parser: 'babel',
      },
    },
    {
      files: '*.json',
      options: {
        parser: 'json',
      },
    },
  ],
}
