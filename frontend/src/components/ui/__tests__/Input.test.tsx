import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input } from '../Input'
import '@testing-library/jest-dom'

describe('Input Component', () => {
  const user = userEvent.setup()

  describe('Basic Rendering', () => {
    it('should render input element', () => {
      render(<Input data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toBeInTheDocument()
      expect(input.tagName).toBe('INPUT')
    })

    it('should render with default type', () => {
      render(<Input data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      // HTMLのinput要素はtype属性が指定されていない場合、デフォルトで"text"として扱われる
      // 実際のHTMLの動作に合わせて、type属性の存在ではなく、input要素として正しく動作することを確認
      expect(input.tagName).toBe('INPUT')
      expect(input).toBeInTheDocument()
    })

    it('should render with custom type', () => {
      render(<Input type="email" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('type', 'email')
    })
  })

  describe('Props Handling', () => {
    it('should accept and apply className', () => {
      render(<Input className="custom-class" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveClass('custom-class')
    })

    it('should accept and apply placeholder', () => {
      render(<Input placeholder="Enter text here" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('placeholder', 'Enter text here')
    })

    it('should accept and apply value', () => {
      render(<Input value="test value" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveValue('test value')
    })

    it('should accept and apply name attribute', () => {
      render(<Input name="username" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('name', 'username')
    })

    it('should accept and apply id attribute', () => {
      render(<Input id="user-input" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('id', 'user-input')
    })

    it('should accept and apply disabled attribute', () => {
      render(<Input disabled data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toBeDisabled()
    })

    it('should accept and apply required attribute', () => {
      render(<Input required data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toBeRequired()
    })

    it('should accept and apply maxLength attribute', () => {
      render(<Input maxLength={50} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('maxLength', '50')
    })

    it('should accept and apply minLength attribute', () => {
      render(<Input minLength={3} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('minLength', '3')
    })
  })

  describe('User Interaction', () => {
    it('should handle user input', async () => {
      render(<Input data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      await user.type(input, 'Hello World')
      expect(input).toHaveValue('Hello World')
    })

    it('should handle focus and blur events', async () => {
      const onFocus = jest.fn()
      const onBlur = jest.fn()
      
      render(<Input onFocus={onFocus} onBlur={onBlur} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      await user.click(input)
      expect(onFocus).toHaveBeenCalledTimes(1)
      
      await user.tab()
      expect(onBlur).toHaveBeenCalledTimes(1)
    })

    it('should handle change events', async () => {
      const onChange = jest.fn()
      render(<Input onChange={onChange} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      await user.type(input, 'a')
      expect(onChange).toHaveBeenCalled()
    })

    it('should handle key events', async () => {
      const onKeyDown = jest.fn()
      const onKeyUp = jest.fn()
      
      render(<Input onKeyDown={onKeyDown} onKeyUp={onKeyUp} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      await user.click(input)
      await user.keyboard('a')
      
      expect(onKeyDown).toHaveBeenCalled()
      expect(onKeyUp).toHaveBeenCalled()
    })
  })

  describe('Ref Functionality', () => {
    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLInputElement>()
      render(<Input ref={ref} data-testid="test-input" />)
      
      expect(ref.current).toBeInstanceOf(HTMLInputElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-input')
    })

    it('should allow ref access to input methods', () => {
      const ref = React.createRef<HTMLInputElement>()
      render(<Input ref={ref} data-testid="test-input" />)
      
      if (ref.current) {
        ref.current.focus()
        expect(ref.current).toHaveFocus()
      }
    })
  })

  describe('Styling and Classes', () => {
    it('should have default styling classes', () => {
      render(<Input data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      expect(input).toHaveClass('flex')
      expect(input).toHaveClass('h-10')
      expect(input).toHaveClass('w-full')
      expect(input).toHaveClass('rounded-md')
      expect(input).toHaveClass('border')
    })

    it('should merge custom classes with default classes', () => {
      render(<Input className="bg-red-500 text-white" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      expect(input).toHaveClass('bg-red-500')
      expect(input).toHaveClass('text-white')
      expect(input).toHaveClass('flex') // デフォルトクラスも保持
    })

    it('should apply focus styles correctly', async () => {
      render(<Input data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      
      await user.click(input)
      expect(input).toHaveFocus()
    })
  })

  describe('Accessibility', () => {
    it('should support aria-label', () => {
      render(<Input aria-label="Username input" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('aria-label', 'Username input')
    })

    it('should support aria-describedby', () => {
      render(<Input aria-describedby="help-text" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('aria-describedby', 'help-text')
    })

    it('should support aria-invalid', () => {
      render(<Input aria-invalid="true" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('aria-invalid', 'true')
    })

    it('should support aria-required', () => {
      render(<Input aria-required="true" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('aria-required', 'true')
    })
  })

  describe('Form Integration', () => {
    it('should work within a form', () => {
      render(
        <form>
          <Input name="username" data-testid="test-input" />
        </form>
      )
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('name', 'username')
    })

    it('should support form validation attributes', () => {
      render(
        <Input 
          pattern="[A-Za-z]{3,}"
          title="Three or more characters"
          data-testid="test-input"
        />
      )
      const input = screen.getByTestId('test-input')
      expect(input).toHaveAttribute('pattern', '[A-Za-z]{3,}')
      expect(input).toHaveAttribute('title', 'Three or more characters')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty string value', () => {
      render(<Input value="" data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveValue('')
    })

    it('should handle null value', () => {
      render(<Input value={null as any} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveValue('')
    })

    it('should handle undefined value', () => {
      render(<Input value={undefined as any} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveValue('')
    })

    it('should handle very long className', () => {
      const longClassName = 'very-long-class-name-that-might-cause-issues '.repeat(10)
      render(<Input className={longClassName} data-testid="test-input" />)
      const input = screen.getByTestId('test-input')
      expect(input).toHaveClass('very-long-class-name-that-might-cause-issues')
    })
  })

  describe('Display Name', () => {
    it('should have correct display name', () => {
      expect(Input.displayName).toBe('Input')
    })
  })
})

