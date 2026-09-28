import axios, {
  type InternalAxiosRequestConfig,
} from 'axios'

import { env } from '../config/env'

type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
}

type RetryableRequestConfig =
  InternalAxiosRequestConfig & {
    _retry?: boolean
  }

export const httpClient = axios.create({
  baseURL: env.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

httpClient.interceptors.request.use((config) => {
  const accessToken =
    localStorage.getItem('access_token')

  if (accessToken) {
    config.headers.Authorization =
      `Bearer ${accessToken}`
  }

  return config
})

let refreshPromise: Promise<string> | null = null

export async function renewAccessToken(): Promise<string> {
  if (refreshPromise) {
    return refreshPromise
  }

  refreshPromise = (async () => {
    const refreshToken =
      localStorage.getItem('refresh_token')

    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const { data } = await axios.post<TokenResponse>(
      `${env.apiUrl}/auth/refresh`,
      {
        refresh_token: refreshToken,
      },
    )

    localStorage.setItem(
      'access_token',
      data.access_token,
    )

    localStorage.setItem(
      'refresh_token',
      data.refresh_token,
    )

    return data.access_token
  })()

  try {
    return await refreshPromise
  } finally {
    refreshPromise = null
  }
}

httpClient.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest =
      error.config as RetryableRequestConfig | undefined

    const isUnauthorized =
      error.response?.status === 401

    const isAuthenticationRequest =
      originalRequest?.url?.includes('/auth/login') ||
      originalRequest?.url?.includes('/auth/register') ||
      originalRequest?.url?.includes('/auth/refresh')

    if (
      !isUnauthorized ||
      !originalRequest ||
      originalRequest._retry ||
      isAuthenticationRequest
    ) {
      return Promise.reject(error)
    }

    originalRequest._retry = true

    try {
      const newAccessToken =
        await renewAccessToken()

      originalRequest.headers.Authorization =
        `Bearer ${newAccessToken}`

      return httpClient(originalRequest)
    } catch (refreshError) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')

      window.location.href = '/iniciar-sesion'

      return Promise.reject(refreshError)
    }
  },
)