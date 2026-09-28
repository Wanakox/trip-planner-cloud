type AccessTokenPayload = {
  exp?: number
  type?: string
}

function decodeAccessToken(token: string): AccessTokenPayload | null {
  try {
    const encodedPayload = token.split('.')[1]
    if (!encodedPayload) return null

    const base64 = encodedPayload
      .replace(/-/g, '+')
      .replace(/_/g, '/')
      .padEnd(Math.ceil(encodedPayload.length / 4) * 4, '=')

    return JSON.parse(atob(base64)) as AccessTokenPayload
  } catch {
    return null
  }
}

export function hasValidAccessToken() {
  const token = localStorage.getItem('access_token')
  if (!token) return false

  const payload = decodeAccessToken(token)

  return Boolean(
    payload &&
      payload.type === 'access' &&
      typeof payload.exp === 'number' &&
      payload.exp * 1000 > Date.now(),
  )
}

export function clearStoredSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}
