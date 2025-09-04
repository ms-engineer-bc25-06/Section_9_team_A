/// <reference types="jest" />
/// <reference types="@testing-library/jest-dom" />
/// <reference types="node" />

declare global {
  // Node.jsのグローバル型
  var global: typeof globalThis
  var process: NodeJS.Process
  
  // Jestのグローバル関数
  var describe: jest.Describe
  var it: jest.It
  var test: jest.It
  var expect: jest.Expect
  var beforeEach: jest.Lifecycle
  var afterEach: jest.Lifecycle
  var beforeAll: jest.Lifecycle
  var afterAll: jest.Lifecycle
  var jest: jest.Jest

  // Jestのマッチャーを拡張
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
      toBeVisible(): R
      toBeHidden(): R
      
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
      toHaveProperty(prop: string, value?: any): R
      
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
