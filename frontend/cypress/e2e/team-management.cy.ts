describe('Team Management Tests', () => {
  beforeEach(() => {
    cy.visit('/team')
  })

  it('should display team page', () => {
    cy.get('h1').should('contain', 'Team')
    cy.get('[data-testid="team-content"]').should('exist')
  })

  it('should show team members list', () => {
    cy.get('[data-testid="team-members"]').should('exist')
  })

  it('should display team creation form', () => {
    cy.get('[data-testid="create-team-form"]').should('exist')
    cy.get('input[name="teamName"]').should('exist')
    cy.get('button[type="submit"]').should('exist')
  })

  it('should show team settings', () => {
    cy.get('[data-testid="team-settings"]').should('exist')
  })

  it('should navigate to member details', () => {
    cy.get('[data-testid="member-item"]').first().click()
    cy.url().should('include', '/team/')
  })
})
