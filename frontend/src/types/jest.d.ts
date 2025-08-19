/// <reference types="jest" />
/// <reference types="@testing-library/jest-dom" />

import '@testing-library/jest-dom'

declare global {
  const jest: typeof import('jest')
  
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R
      toHaveClass(className: string): R
      toBeDisabled(): R
      toHaveBeenCalled(): R
      toHaveBeenCalledTimes(times: number): R
    }
  }
}

export {}
