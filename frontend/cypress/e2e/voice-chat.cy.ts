// 音声チャットの最小E2E（UIとWS接続のスモーク）

describe('Voice Chat Room', () => {
  const roomId = 'e2e-room-1'

  it('should render room page and show connecting status', () => {
    cy.visit(`/voice-chat/${roomId}`)
    cy.contains('Room').should('exist')
    cy.contains('接続中').should('exist')
  })
})


