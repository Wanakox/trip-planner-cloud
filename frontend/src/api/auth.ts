import { httpClient } from './http'

export type RegisterPayload = {
  name: string
  surname: string
  username: string
  email: string
  password: string
  default_currency: string
}

export type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

export async function registerUser(payload: RegisterPayload) {
  const { data } = await httpClient.post('/auth/register', payload)
  return data
}

export async function loginUser(identifier: string, password: string) {
  const { data } = await httpClient.post<TokenResponse>('/auth/login', { identifier, password })
  return data
}

export async function verifyEmail(token: string) {
  await httpClient.post('/auth/verify-email', { token })
}

export async function resendVerification(email: string) {
  await httpClient.post('/auth/resend-verification', { email })
}
