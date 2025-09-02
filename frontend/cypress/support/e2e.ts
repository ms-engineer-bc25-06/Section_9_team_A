// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// グローバル設定
Cypress.on('uncaught:exception', (err, runnable) => {
  // テストで予期しないエラーを無視
  return false
})

// カスタムコマンドの型定義
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * カスタムコマンド: ログイン
       * @example cy.login('test@example.com', 'password123')
       */
      login(email: string, password: string): Chainable<void>
      
      /**
       * カスタムコマンド: ログアウト
       * @example cy.logout()
       */
      logout(): Chainable<void>
      
      /**
       * カスタムコマンド: データ属性で要素を取得
       * @example cy.getByTestId('login-button')
       */
      getByTestId(testId: string): Chainable<JQuery<HTMLElement>>
    }
  }
}
