describe('Analytics Tests', () => {
  beforeEach(() => {
    cy.visit('/analytics')
  })

  it('should display analytics page', () => {
    cy.get('h1').should('contain', 'Analytics')
    cy.get('[data-testid="analytics-content"]').should('exist')
  })

  it('should show analytics dashboard', () => {
    cy.get('[data-testid="analytics-dashboard"]').should('exist')
  })

  it('should display communication charts', () => {
    cy.get('[data-testid="communication-charts"]').should('exist')
  })

  it('should show sentiment analysis', () => {
    cy.get('[data-testid="sentiment-analysis"]').should('exist')
  })

  it('should navigate to reports page', () => {
    cy.contains('レポート').click()
    cy.url().should('include', '/analytics/reports')
  })
})
