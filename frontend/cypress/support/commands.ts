// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// カスタムコマンド: ログイン
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login')
  cy.getByTestId('email-input').type(email)
  cy.getByTestId('password-input').type(password)
  cy.getByTestId('login-button').click()
  
  // ログイン成功の確認
  cy.url().should('not.include', '/login')
  cy.getByTestId('user-menu').should('be.visible')
})

// カスタムコマンド: ログアウト
Cypress.Commands.add('logout', () => {
  cy.getByTestId('user-menu').click()
  cy.getByTestId('logout-button').click()
  
  // ログアウト成功の確認
  cy.url().should('include', '/login')
  cy.getByTestId('login-form').should('be.visible')
})

// カスタムコマンド: データ属性で要素を取得
Cypress.Commands.add('getByTestId', (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`)
})

// カスタムコマンド: 要素が表示されるまで待機
Cypress.Commands.add('waitForElement', (selector: string, timeout: number = 10000) => {
  return cy.get(selector, { timeout }).should('be.visible')
})

// カスタムコマンド: ページ遷移の待機
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('body').should('not.have.class', 'loading')
  cy.get('[data-testid="loading-spinner"]').should('not.exist')
})

// カスタムコマンド: フォームの入力と送信
Cypress.Commands.add('fillAndSubmitForm', (formData: Record<string, string>) => {
  Object.entries(formData).forEach(([field, value]) => {
    cy.getByTestId(`${field}-input`).clear().type(value)
  })
  cy.getByTestId('submit-button').click()
})

// カスタムコマンド: モーダルの確認
Cypress.Commands.add('confirmModal', () => {
  cy.getByTestId('modal-confirm-button').click()
})

// カスタムコマンド: モーダルのキャンセル
Cypress.Commands.add('cancelModal', () => {
  cy.getByTestId('modal-cancel-button').click()
})

// カスタムコマンド: 通知の確認
Cypress.Commands.add('checkNotification', (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  cy.getByTestId(`notification-${type}`).should('contain', message)
})

// カスタムコマンド: レスポンシブテスト
Cypress.Commands.add('testResponsive', (viewport: 'mobile' | 'tablet' | 'desktop') => {
  const viewports = {
    mobile: { width: 375, height: 667 },
    tablet: { width: 768, height: 1024 },
    desktop: { width: 1280, height: 720 }
  }
  
  cy.viewport(viewports[viewport].width, viewports[viewport].height)
})

// カスタムコマンド: APIモックの設定
// Cypress.Commands.add('mockApi', (method: string, url: string, response: any, statusCode: number = 200) => {
//   cy.intercept(method, url, {
//     statusCode,
//     body: response
//   }).as(`${method.toLowerCase()}_${url.replace(/\//g, '_')}`)
// })

// カスタムコマンド: ファイルアップロード
// Cypress.Commands.add('uploadFile', (selector: string, filePath: string) => {
//   cy.get(selector).attachFile(filePath)
// })

// カスタムコマンド: キーボードショートカット
Cypress.Commands.add('pressKey', (key: string) => {
  cy.get('body').type(key)
})

// カスタムコマンド: スクロール
Cypress.Commands.add('scrollToElement', (selector: string) => {
  cy.get(selector).scrollIntoView()
})

// カスタムコマンド: 要素の存在確認
Cypress.Commands.add('shouldExist', (selector: string) => {
  cy.get(selector).should('exist')
})

// カスタムコマンド: 要素の非存在確認
Cypress.Commands.add('shouldNotExist', (selector: string) => {
  cy.get(selector).should('not.exist')
})
