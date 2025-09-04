import React from 'react'
import { render, screen } from '@testing-library/react'
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter 
} from '../Card'
import '@testing-library/jest-dom'

describe('Card Components', () => {
  describe('Card Component', () => {
    it('should render card element', () => {
      render(<Card data-testid="test-card" />)
      const card = screen.getByTestId('test-card')
      expect(card).toBeInTheDocument()
      expect(card.tagName).toBe('DIV')
    })

    it('should accept and apply className', () => {
      render(<Card className="custom-card" data-testid="test-card" />)
      const card = screen.getByTestId('test-card')
      expect(card).toHaveClass('custom-card')
    })

    it('should have default styling classes', () => {
      render(<Card data-testid="test-card" />)
      const card = screen.getByTestId('test-card')
      
      expect(card).toHaveClass('rounded-lg')
      expect(card).toHaveClass('border')
      expect(card).toHaveClass('bg-card')
      expect(card).toHaveClass('text-card-foreground')
      expect(card).toHaveClass('shadow-sm')
    })

    it('should merge custom classes with default classes', () => {
      render(<Card className="bg-blue-500 text-white" data-testid="test-card" />)
      const card = screen.getByTestId('test-card')
      
      expect(card).toHaveClass('bg-blue-500')
      expect(card).toHaveClass('text-white')
      expect(card).toHaveClass('rounded-lg') // デフォルトクラスも保持
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<Card ref={ref} data-testid="test-card" />)
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-card')
    })

    it('should accept children', () => {
      render(
        <Card data-testid="test-card">
          <div data-testid="card-child">Card Content</div>
        </Card>
      )
      
      const card = screen.getByTestId('test-card')
      const child = screen.getByTestId('card-child')
      
      expect(card).toContainElement(child)
      expect(child).toHaveTextContent('Card Content')
    })

    it('should have correct display name', () => {
      expect(Card.displayName).toBe('Card')
    })
  })

  describe('CardHeader Component', () => {
    it('should render card header element', () => {
      render(<CardHeader data-testid="test-header" />)
      const header = screen.getByTestId('test-header')
      expect(header).toBeInTheDocument()
      expect(header.tagName).toBe('DIV')
    })

    it('should accept and apply className', () => {
      render(<CardHeader className="custom-header" data-testid="test-header" />)
      const header = screen.getByTestId('test-header')
      expect(header).toHaveClass('custom-header')
    })

    it('should have default styling classes', () => {
      render(<CardHeader data-testid="test-header" />)
      const header = screen.getByTestId('test-header')
      
      expect(header).toHaveClass('flex')
      expect(header).toHaveClass('flex-col')
      expect(header).toHaveClass('space-y-1.5')
      expect(header).toHaveClass('p-6')
    })

    it('should merge custom classes with default classes', () => {
      render(<CardHeader className="bg-gray-100" data-testid="test-header" />)
      const header = screen.getByTestId('test-header')
      
      expect(header).toHaveClass('bg-gray-100')
      expect(header).toHaveClass('flex') // デフォルトクラスも保持
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<CardHeader ref={ref} data-testid="test-header" />)
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-header')
    })

    it('should accept children', () => {
      render(
        <CardHeader data-testid="test-header">
          <div data-testid="header-child">Header Content</div>
        </CardHeader>
      )
      
      const header = screen.getByTestId('test-header')
      const child = screen.getByTestId('header-child')
      
      expect(header).toContainElement(child)
      expect(child).toHaveTextContent('Header Content')
    })

    it('should have correct display name', () => {
      expect(CardHeader.displayName).toBe('CardHeader')
    })
  })

  describe('CardTitle Component', () => {
    it('should render card title element', () => {
      render(<CardTitle data-testid="test-title" />)
      const title = screen.getByTestId('test-title')
      expect(title).toBeInTheDocument()
      expect(title.tagName).toBe('H3')
    })

    it('should accept and apply className', () => {
      render(<CardTitle className="custom-title" data-testid="test-title" />)
      const title = screen.getByTestId('test-title')
      expect(title).toHaveClass('custom-title')
    })

    it('should have default styling classes', () => {
      render(<CardTitle data-testid="test-title" />)
      const title = screen.getByTestId('test-title')
      
      expect(title).toHaveClass('text-2xl')
      expect(title).toHaveClass('font-semibold')
      expect(title).toHaveClass('leading-none')
      expect(title).toHaveClass('tracking-tight')
    })

    it('should merge custom classes with default classes', () => {
      render(<CardTitle className="text-red-500" data-testid="test-title" />)
      const title = screen.getByTestId('test-title')
      
      expect(title).toHaveClass('text-red-500')
      expect(title).toHaveClass('text-2xl') // デフォルトクラスも保持
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLHeadingElement>()
      render(<CardTitle ref={ref} data-testid="test-title" />)
      
      expect(ref.current).toBeInstanceOf(HTMLHeadingElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-title')
    })

    it('should accept children', () => {
      render(
        <CardTitle data-testid="test-title">
          Card Title Text
        </CardTitle>
      )
      
      const title = screen.getByTestId('test-title')
      expect(title).toHaveTextContent('Card Title Text')
    })

    it('should have correct display name', () => {
      expect(CardTitle.displayName).toBe('CardTitle')
    })
  })

  describe('CardDescription Component', () => {
    it('should render card description element', () => {
      render(<CardDescription data-testid="test-description" />)
      const description = screen.getByTestId('test-description')
      expect(description).toBeInTheDocument()
      expect(description.tagName).toBe('P')
    })

    it('should accept and apply className', () => {
      render(<CardDescription className="custom-description" data-testid="test-description" />)
      const description = screen.getByTestId('test-description')
      expect(description).toHaveClass('custom-description')
    })

    it('should have default styling classes', () => {
      render(<CardDescription data-testid="test-description" />)
      const description = screen.getByTestId('test-description')
      
      expect(description).toHaveClass('text-sm')
      expect(description).toHaveClass('text-muted-foreground')
    })

    it('should merge custom classes with default classes', () => {
      render(<CardDescription className="text-blue-500" data-testid="test-description" />)
      const description = screen.getByTestId('test-description')
      
      expect(description).toHaveClass('text-blue-500')
      expect(description).toHaveClass('text-sm') // デフォルトクラスも保持
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLParagraphElement>()
      render(<CardDescription ref={ref} data-testid="test-description" />)
      
      expect(ref.current).toBeInstanceOf(HTMLParagraphElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-description')
    })

    it('should accept children', () => {
      render(
        <CardDescription data-testid="test-description">
          Card description text
        </CardDescription>
      )
      
      const description = screen.getByTestId('test-description')
      expect(description).toHaveTextContent('Card description text')
    })

    it('should have correct display name', () => {
      expect(CardDescription.displayName).toBe('CardDescription')
    })
  })

  describe('CardContent Component', () => {
    it('should render card content element', () => {
      render(<CardContent data-testid="test-content" />)
      const content = screen.getByTestId('test-content')
      expect(content).toBeInTheDocument()
      expect(content.tagName).toBe('DIV')
    })

    it('should accept and apply className', () => {
      render(<CardContent className="custom-content" data-testid="test-content" />)
      const content = screen.getByTestId('test-content')
      expect(content).toHaveClass('custom-content')
    })

    it('should have default styling classes', () => {
      render(<CardContent data-testid="test-content" />)
      const content = screen.getByTestId('test-content')
      
      expect(content).toHaveClass('p-6')
      expect(content).toHaveClass('pt-0')
    })

    it('should merge custom classes with default classes', () => {
      render(<CardContent className="bg-gray-50" data-testid="test-content" />)
      const content = screen.getByTestId('test-content')
      
      expect(content).toHaveClass('bg-gray-50')
      expect(content).toHaveClass('p-6') // デフォルトクラスも保持
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<CardContent ref={ref} data-testid="test-content" />)
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-content')
    })

    it('should accept children', () => {
      render(
        <CardContent data-testid="test-content">
          <div data-testid="content-child">Content text</div>
        </CardContent>
      )
      
      const content = screen.getByTestId('test-content')
      const child = screen.getByTestId('content-child')
      
      expect(content).toContainElement(child)
      expect(child).toHaveTextContent('Content text')
    })

    it('should have correct display name', () => {
      expect(CardContent.displayName).toBe('CardContent')
    })
  })

  describe('CardFooter Component', () => {
    it('should render card footer element', () => {
      render(<CardFooter data-testid="test-footer" />)
      const footer = screen.getByTestId('test-footer')
      expect(footer).toBeInTheDocument()
      expect(footer.tagName).toBe('DIV')
    })

    it('should accept and apply className', () => {
      render(<CardFooter className="custom-footer" data-testid="test-footer" />)
      const footer = screen.getByTestId('test-footer')
      expect(footer).toHaveClass('custom-footer')
    })

    it('should have default styling classes', () => {
      render(<CardFooter data-testid="test-footer" />)
      const footer = screen.getByTestId('test-footer')
      
      expect(footer).toHaveClass('flex')
      expect(footer).toHaveClass('items-center')
      expect(footer).toHaveClass('p-6')
      expect(footer).toHaveClass('pt-0')
    })

    it('should merge custom classes with default classes', () => {
      render(<CardFooter className="justify-end" data-testid="test-footer" />)
      const footer = screen.getByTestId('test-footer')
      
      expect(footer).toHaveClass('justify-end')
      expect(footer).toHaveClass('flex') // デフォルトクラスも保持
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<CardFooter ref={ref} data-testid="test-footer" />)
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
      expect(ref.current).toHaveAttribute('data-testid', 'test-footer')
    })

    it('should accept children', () => {
      render(
        <CardFooter data-testid="test-footer">
          <button data-testid="footer-button">Action</button>
        </CardFooter>
      )
      
      const footer = screen.getByTestId('test-footer')
      const button = screen.getByTestId('footer-button')
      
      expect(footer).toContainElement(button)
      expect(button).toHaveTextContent('Action')
    })

    it('should have correct display name', () => {
      expect(CardFooter.displayName).toBe('CardFooter')
    })
  })

  describe('Card Composition', () => {
    it('should work together as a complete card', () => {
      render(
        <Card data-testid="complete-card">
          <CardHeader data-testid="complete-header">
            <CardTitle data-testid="complete-title">Card Title</CardTitle>
            <CardDescription data-testid="complete-description">
              Card description
            </CardDescription>
          </CardHeader>
          <CardContent data-testid="complete-content">
            <p>Main content area</p>
          </CardContent>
          <CardFooter data-testid="complete-footer">
            <button>Save</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByTestId('complete-card')).toBeInTheDocument()
      expect(screen.getByTestId('complete-header')).toBeInTheDocument()
      expect(screen.getByTestId('complete-title')).toHaveTextContent('Card Title')
      expect(screen.getByTestId('complete-description')).toHaveTextContent('Card description')
      expect(screen.getByTestId('complete-content')).toHaveTextContent('Main content area')
      expect(screen.getByTestId('complete-footer')).toHaveTextContent('Save')
    })

    it('should handle nested card structures', () => {
      render(
        <Card data-testid="outer-card">
          <CardContent>
            <Card data-testid="inner-card">
              <CardContent>Nested content</CardContent>
            </Card>
          </CardContent>
        </Card>
      )

      expect(screen.getByTestId('outer-card')).toBeInTheDocument()
      expect(screen.getByTestId('inner-card')).toBeInTheDocument()
      expect(screen.getByText('Nested content')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Card data-testid="empty-card" />)
      const card = screen.getByTestId('empty-card')
      expect(card).toBeInTheDocument()
      expect(card.children).toHaveLength(0)
    })

    it('should handle very long className', () => {
      const longClassName = 'very-long-class-name-that-might-cause-issues '.repeat(10)
      render(<Card className={longClassName} data-testid="test-card" />)
      const card = screen.getByTestId('test-card')
      expect(card).toHaveClass('very-long-class-name-that-might-cause-issues')
    })

    it('should handle null and undefined props', () => {
      render(<Card className={null as any} data-testid="test-card" />)
      const card = screen.getByTestId('test-card')
      expect(card).toBeInTheDocument()
    })
  })
})


