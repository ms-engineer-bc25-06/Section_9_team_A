describe('Basic Application Test', () => {
  beforeEach(() => {
    // 各テストの前にアプリケーションのルートページにアクセス
    cy.visit('/')
  })

  it('should load the main page', () => {
    // メインページが正常に読み込まれることを確認
    cy.get('body').should('be.visible')
  })

  it('should have navigation elements', () => {
    // 基本的なナビゲーション要素が存在することを確認
    cy.get('nav').should('exist')
  })

  it('should be responsive', () => {
    // レスポンシブデザインのテスト
    // モバイルサイズ
    cy.viewport(375, 667)
    cy.get('body').should('be.visible')
    
    // タブレットサイズ
    cy.viewport(768, 1024)
    cy.get('body').should('be.visible')
    
    // デスクトップサイズ
    cy.viewport(1920, 1080)
    cy.get('body').should('be.visible')
  })
})
