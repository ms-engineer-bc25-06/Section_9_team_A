describe('Voice Chat Tests', () => {
  beforeEach(() => {
    cy.visit('/voice-chat')
  })

  it('should display voice chat page', () => {
    cy.get('h1').should('contain', 'Voice Chat')
    cy.get('[data-testid="voice-chat-content"]').should('exist')
  })

  it('should show voice chat rooms', () => {
    cy.get('[data-testid="voice-chat-rooms"]').should('exist')
  })

  it('should display room creation form', () => {
    cy.get('[data-testid="create-room-form"]').should('exist')
    cy.get('input[name="roomName"]').should('exist')
    cy.get('button[type="submit"]').should('exist')
  })

  it('should show room history', () => {
    cy.get('[data-testid="room-history"]').should('exist')
  })

  it('should navigate to specific room', () => {
    cy.get('[data-testid="room-item"]').first().click()
    cy.url().should('include', '/voice-chat/')
  })
})
