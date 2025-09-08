import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from '@jest/globals'

describe('ProtectedRoute', () => {
  it('should have at least one test', () => {
    expect(true).toBe(true)
  })

  it('should be a placeholder test', () => {
    // TODO:実際のテストは後で実装予定
    const placeholder = 'placeholder'
    expect(placeholder).toBe('placeholder')
  })
})
