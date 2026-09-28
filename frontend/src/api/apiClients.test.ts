import { beforeEach, describe, expect, it, vi } from 'vitest'

import { loginUser, registerUser } from './auth'
import { convertCurrency, getCurrencies } from './currency'
import { searchFlights } from './flights'
import { getHealth } from './health'
import { httpClient } from './http'
import { deleteCurrentUser, getCurrentUser, updateCurrentUser, uploadCurrentUserPhoto } from './user'

describe('clientes API', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('envía registro y login a sus rutas', async () => {
    const post = vi.spyOn(httpClient, 'post').mockResolvedValue({ data: { ok: true } })
    await registerUser({ name: 'Ana', surname: 'López', username: 'ana', email: 'ana@test.es', password: 'Password1!', default_currency: 'EUR' })
    expect(post).toHaveBeenNthCalledWith(1, '/auth/register', expect.objectContaining({ username: 'ana' }))
    await loginUser('ana', 'Password1!')
    expect(post).toHaveBeenNthCalledWith(2, '/auth/login', { identifier: 'ana', password: 'Password1!' })
  })

  it('consulta monedas y conversión con todos los parámetros', async () => {
    const get = vi.spyOn(httpClient, 'get').mockResolvedValue({ data: [] })
    await getCurrencies()
    expect(get).toHaveBeenNthCalledWith(1, '/currencies')
    await convertCurrency(100, 'EUR', 'USD')
    expect(get).toHaveBeenNthCalledWith(2, '/currencies/convert', { params: { amount: 100, from_currency: 'EUR', to_currency: 'USD' } })
  })

  it('envía todos los filtros de búsqueda de vuelos', async () => {
    const get = vi.spyOn(httpClient, 'get').mockResolvedValue({ data: { offers: [] } })
    const params = { origin: 'MAD', destination: 'HER', departure_date: '2026-09-01', adults: 2, cabin_class: 'economy' as const }
    await searchFlights(params)
    expect(get).toHaveBeenCalledWith('/flights/search', { params })
  })

  it('consulta el estado de salud', async () => {
    vi.spyOn(httpClient, 'get').mockResolvedValue({ data: { status: 'ok', database: 'ok' } })
    await expect(getHealth()).resolves.toEqual({ status: 'ok', database: 'ok' })
  })

  it('gestiona lectura, edición y borrado del perfil', async () => {
    const profile = { id: 1, name: 'Ana', surname: 'López', username: 'ana', email: 'ana@test.es', default_currency: 'EUR', profile_photo: null }
    const get = vi.spyOn(httpClient, 'get').mockResolvedValue({ data: profile })
    const patch = vi.spyOn(httpClient, 'patch').mockResolvedValue({ data: profile })
    const del = vi.spyOn(httpClient, 'delete').mockResolvedValue({ data: undefined })
    await expect(getCurrentUser()).resolves.toEqual(profile)
    await updateCurrentUser(profile)
    await deleteCurrentUser()
    expect(get).toHaveBeenCalledWith('/users/me')
    expect(patch).toHaveBeenCalledWith('/users/me', profile)
    expect(del).toHaveBeenCalledWith('/users/me')
  })

  it('sube la foto como multipart', async () => {
    const post = vi.spyOn(httpClient, 'post').mockResolvedValue({ data: {} })
    const file = new File(['imagen'], 'perfil.png', { type: 'image/png' })
    await uploadCurrentUserPhoto(file)
    const body = post.mock.calls[0]?.[1] as FormData
    expect(post.mock.calls[0]?.[0]).toBe('/users/me/profile-photo')
    expect(body.get('photo')).toBe(file)
  })
})
