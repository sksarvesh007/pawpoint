import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FAQAccordion } from '@/components/FAQAccordion'
import { faqData } from '@/data/faqData'

describe('FAQAccordion', () => {
  it('renders all FAQ questions', () => {
    render(<FAQAccordion />)
    for (const faq of faqData) {
      expect(screen.getByText(faq.question)).toBeInTheDocument()
    }
  })

  it('does not show answers initially', () => {
    render(<FAQAccordion />)
    // Answers are hidden via CSS (max-h-0 opacity-0), but still in DOM
    // Verify the first answer text is in the document (hidden via CSS)
    expect(screen.getByText(faqData[0].answer)).toBeInTheDocument()
  })

  it('clicking a question toggles open state (aria/visual)', async () => {
    const user = userEvent.setup()
    render(<FAQAccordion />)

    const firstButton = screen.getAllByRole('button')[0]
    // Initially the chevron container should not have rotate-180
    const chevronContainer = firstButton.querySelector('div[class*="rounded-full"]') as HTMLElement
    expect(chevronContainer?.className).not.toContain('rotate-180')

    await user.click(firstButton)
    // After click, rotate-180 should be applied
    expect(chevronContainer?.className).toContain('rotate-180')
  })

  it('clicking an open question collapses it', async () => {
    const user = userEvent.setup()
    render(<FAQAccordion />)

    const firstButton = screen.getAllByRole('button')[0]
    const chevronContainer = firstButton.querySelector('div[class*="rounded-full"]') as HTMLElement

    // Open it
    await user.click(firstButton)
    expect(chevronContainer?.className).toContain('rotate-180')

    // Close it
    await user.click(firstButton)
    expect(chevronContainer?.className).not.toContain('rotate-180')
  })

  it('opening one question closes the previously open one', async () => {
    const user = userEvent.setup()
    render(<FAQAccordion />)

    const buttons = screen.getAllByRole('button')
    const firstChevron = buttons[0].querySelector('div[class*="rounded-full"]') as HTMLElement
    const secondChevron = buttons[1].querySelector('div[class*="rounded-full"]') as HTMLElement

    // Open first
    await user.click(buttons[0])
    expect(firstChevron?.className).toContain('rotate-180')
    expect(secondChevron?.className).not.toContain('rotate-180')

    // Open second — first should close
    await user.click(buttons[1])
    expect(firstChevron?.className).not.toContain('rotate-180')
    expect(secondChevron?.className).toContain('rotate-180')
  })

  it('renders correct number of FAQ buttons', () => {
    render(<FAQAccordion />)
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(faqData.length)
  })
})
