import {
  useEffect,
  useState,
} from 'react'
import {
  Navigate,
  Outlet,
  useLocation,
} from 'react-router-dom'
import {
  Box,
  CircularProgress,
} from '@mui/material'

import { renewAccessToken } from '../api/http'
import {
  clearStoredSession,
  hasValidAccessToken,
} from '../utils/authSession'

type AuthenticationState =
  | 'checking'
  | 'authenticated'
  | 'unauthenticated'

export function ProtectedRoute() {
  const location = useLocation()

  const [authenticationState, setAuthenticationState] =
    useState<AuthenticationState>('checking')

  useEffect(() => {
    let active = true

    async function checkAuthentication() {
      if (hasValidAccessToken()) {
        if (active) {
          setAuthenticationState('authenticated')
        }

        return
      }

      const refreshToken =
        localStorage.getItem('refresh_token')

      if (!refreshToken) {
        clearStoredSession()

        if (active) {
          setAuthenticationState('unauthenticated')
        }

        return
      }

      try {
        await renewAccessToken()

        if (active) {
          setAuthenticationState('authenticated')
        }
      } catch {
        clearStoredSession()

        if (active) {
          setAuthenticationState('unauthenticated')
        }
      }
    }

    void checkAuthentication()

    return () => {
      active = false
    }
  }, [])

  if (authenticationState === 'checking') {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  if (authenticationState === 'unauthenticated') {
    return (
      <Navigate
        to="/iniciar-sesion"
        replace
        state={{
          from: location.pathname,
        }}
      />
    )
  }

  return <Outlet />
}