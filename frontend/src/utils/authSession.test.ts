import { afterEach, describe, expect, it, vi } from 'vitest'

import { clearStoredSession, hasValidAccessToken } from './authSession'

function token(payload: object) {
  const encoded = btoa(JSON.stringify(payload)).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_')
  return `header.${encoded}.signature`
}

describe('authSession', () => {
  afterEach(() => vi.useRealTimers())

  it('acepta un access token vigente', () => {
    vi.setSystemTime(new Date('2026-08-30T12:00:00Z'))
    localStorage.setItem('access_token', token({ type: 'access', exp: 1788094800 }))
    expect(hasValidAccessToken()).toBe(true)
  })

  it.each([
    ['sin token', null],
    ['token ilegible', 'incorrecto'],
    ['refresh token', token({ type: 'refresh', exp: 4102444800 })],
    ['token caducado', token({ type: 'access', exp: 1 })],
    ['token sin expiración', token({ type: 'access' })],
  ])('rechaza %s', (_label, value) => {
    if (value) localStorage.setItem('access_token', value)
    expect(hasValidAccessToken()).toBe(false)
  })

  it('elimina ambos tokens de sesión', () => {
    localStorage.setItem('access_token', 'a')
    localStorage.setItem('refresh_token', 'r')
    clearStoredSession()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
