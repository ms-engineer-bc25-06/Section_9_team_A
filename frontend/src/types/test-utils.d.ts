import '@testing-library/jest-dom'

declare global {
  namespace jest {
    interface Matchers<R> {
      // Jest DOM matchers
      toBeInTheDocument(): R
      toHaveClass(className: string): R
      toHaveAttribute(attr: string, value?: string): R
      toHaveValue(value: string | number | string[]): R
      toBeDisabled(): R
      toBeRequired(): R
      toHaveFocus(): R
      toContainElement(element: Element | null): R
      toHaveTextContent(text: string | RegExp): R
      
      // Jest core matchers
      toBe(value: any): R
      toEqual(value: any): R
      toBeNull(): R
      toBeDefined(): R
      toBeUndefined(): R
      toBeTruthy(): R
      toBeFalsy(): R
      toContain(value: any): R
      toHaveLength(length: number): R
      toBeInstanceOf(constructor: any): R
      toMatch(regexp: RegExp | string): R
      toThrow(error?: string | RegExp | Error): R
      
      // Mock matchers
      toHaveBeenCalled(): R
      toHaveBeenCalledTimes(times: number): R
      toHaveBeenCalledWith(...args: any[]): R
      toHaveBeenLastCalledWith(...args: any[]): R
      toHaveBeenNthCalledWith(n: number, ...args: any[]): R
      toHaveReturned(): R
      toHaveReturnedTimes(times: number): R
      toHaveReturnedWith(value: any): R
      toHaveLastReturnedWith(value: any): R
      toHaveNthReturnedWith(n: number, value: any): R
    }
  }
}

export {}
