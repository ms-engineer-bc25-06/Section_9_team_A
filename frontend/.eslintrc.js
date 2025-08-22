module.exports = {
  extends: [
    'next/core-web-vitals',
  ],
  
  rules: {
    'no-console': 'warn',
  },
  
  env: {
    browser: true,
    es2021: true,
    node: true,
    jest: true,
  },
}
