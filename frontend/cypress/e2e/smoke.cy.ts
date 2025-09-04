describe('Smoke Test', () => {
  it('should visit the homepage', () => {
    cy.visit('/')
    cy.get('body').should('exist')
  })

  it('should have basic page structure', () => {
    cy.visit('/')
    cy.get('html').should('exist')
    cy.get('head').should('exist')
    cy.get('body').should('exist')
  })
})
