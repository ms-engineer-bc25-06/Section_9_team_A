/// <reference types="cypress" />

declare namespace Cypress {
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
    
    /**
     * カスタムコマンド: 要素が表示されるまで待機
     * @example cy.waitForElement('.loading-spinner')
     */
    waitForElement(selector: string, timeout?: number): Chainable<JQuery<HTMLElement>>
    
    /**
     * カスタムコマンド: ページ遷移の待機
     * @example cy.waitForPageLoad()
     */
    waitForPageLoad(): Chainable<void>
    
    /**
     * カスタムコマンド: フォームの入力と送信
     * @example cy.fillAndSubmitForm({ email: 'test@example.com', password: '123' })
     */
    fillAndSubmitForm(formData: Record<string, string>): Chainable<void>
    
    /**
     * カスタムコマンド: モーダルの確認
     * @example cy.confirmModal()
     */
    confirmModal(): Chainable<void>
    
    /**
     * カスタムコマンド: モーダルのキャンセル
     * @example cy.cancelModal()
     */
    cancelModal(): Chainable<void>
    
    /**
     * カスタムコマンド: 通知の確認
     * @example cy.checkNotification('Login successful', 'success')
     */
    checkNotification(message: string, type?: 'success' | 'error' | 'info'): Chainable<void>
    
    /**
     * カスタムコマンド: レスポンシブテスト
     * @example cy.testResponsive('mobile')
     */
    testResponsive(viewport: 'mobile' | 'tablet' | 'desktop'): Chainable<void>
    
    /**
     * カスタムコマンド: APIモックの設定
     * @example cy.mockApi('GET', '/api/users', { users: [] })
     */
    mockApi(method: string, url: string, response: any, statusCode?: number): Chainable<void>
    
    /**
     * カスタムコマンド: ファイルアップロード
     * @example cy.uploadFile('.file-input', 'test-file.txt')
     */
    uploadFile(selector: string, filePath: string): Chainable<void>
    
    /**
     * カスタムコマンド: キーボードショートカット
     * @example cy.pressKey('{enter}')
     */
    pressKey(key: string): Chainable<void>
    
    /**
     * カスタムコマンド: スクロール
     * @example cy.scrollToElement('.footer')
     */
    scrollToElement(selector: string): Chainable<void>
    
    /**
     * カスタムコマンド: 要素の存在確認
     * @example cy.shouldExist('.header')
     */
    shouldExist(selector: string): Chainable<void>
    
    /**
     * カスタムコマンド: 要素の非存在確認
     * @example cy.shouldNotExist('.error-message')
     */
    shouldNotExist(selector: string): Chainable<void>
  }
}
