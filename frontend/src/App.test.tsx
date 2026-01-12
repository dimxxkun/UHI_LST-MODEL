import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '@/App'

describe('App Integration', () => {
    it('renders the dashboard layout by default', async () => {
        render(<App />)

        // Check for Sidebar link
        expect(screen.getByRole('link', { name: /Analysis/i })).toBeInTheDocument()

        // Check for Dashboard heading (verifies page content)
        expect(screen.getByRole('heading', { name: /Dashboard/i })).toBeInTheDocument()
    })
})
