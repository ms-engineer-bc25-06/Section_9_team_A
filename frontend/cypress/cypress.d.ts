/// <reference types="cypress" />

// Cypressのグローバル型定義
declare global {
  namespace Cypress {
    interface Chainable {
      // カスタムコマンドの型定義
      login(email: string, password: string): Chainable<void>
      logout(): Chainable<void>
      getByTestId(testId: string): Chainable<JQuery<HTMLElement>>
      waitForElement(selector: string, timeout?: number): Chainable<JQuery<HTMLElement>>
      waitForPageLoad(): Chainable<void>
      fillAndSubmitForm(formData: Record<string, string>): Chainable<void>
      confirmModal(): Chainable<void>
      cancelModal(): Chainable<void>
      checkNotification(message: string, type?: 'success' | 'error' | 'info'): Chainable<void>
      testResponsive(viewport: 'mobile' | 'tablet' | 'desktop'): Chainable<void>
      mockApi(method: string, url: string, response: any, statusCode?: number): Chainable<void>
      uploadFile(selector: string, filePath: string): Chainable<void>
      pressKey(key: string): Chainable<void>
      scrollToElement(selector: string): Chainable<void>
      shouldExist(selector: string): Chainable<void>
      shouldNotExist(selector: string): Chainable<void>
    }
  }
}

export {}
