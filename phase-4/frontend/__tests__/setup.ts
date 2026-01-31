// Vitest setup file
import { expect, afterEach } from 'vitest'

// Mock fetch for tests
global.fetch = async (url: string | URL | Request) => {
  // Return mock responses for health endpoints
  const urlString = url.toString()

  if (urlString.includes('/health')) {
    return new Response(JSON.stringify({ status: 'healthy' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  if (urlString.includes('/ready')) {
    return new Response(JSON.stringify({ status: 'ready' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  return new Response('Not Found', { status: 404 })
}

// Clean up after each test
afterEach(() => {
  // Reset any test state if needed
})
