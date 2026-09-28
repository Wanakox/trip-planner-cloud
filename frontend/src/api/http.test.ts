import { describe, expect, it, vi } from 'vitest'

import { httpClient } from './http'

describe('httpClient', () => {
  it('añade el token Bearer cuando existe', async () => {
    localStorage.setItem('access_token', 'token-prueba')
    const adapter = vi.fn(async (config) => ({ data: {}, status: 200, statusText: 'OK', headers: {}, config }))
    await httpClient.get('/test', { adapter })
    expect(adapter.mock.calls[0]?.[0].headers.Authorization).toBe('Bearer token-prueba')
  })

  it('no añade autorización sin sesión', async () => {
    const adapter = vi.fn(async (config) => ({ data: {}, status: 200, statusText: 'OK', headers: {}, config }))
    await httpClient.get('/test', { adapter })
    expect(adapter.mock.calls[0]?.[0].headers.Authorization).toBeUndefined()
  })
})
