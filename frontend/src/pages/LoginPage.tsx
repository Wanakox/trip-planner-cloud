import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Link,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { loginUser } from '../api/auth'
import { AuthCard } from '../components/AuthCard'
import { useAuthTransition } from '../components/AuthTransition'
import { BrandLogo } from '../components/BrandLogo'

export function LoginPage() {
  const navigate = useNavigate()

  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')

  const {
    phase,
    direction,
    isTransitioning,
    startAuthTransition,
  } = useAuthTransition()

  const isLeavingLogin =
    direction === 'toRegister' &&
    (phase === 'fade' || phase === 'cover')

  const mutation = useMutation({
    mutationFn: () => loginUser(identifier, password),
    onSuccess: (tokens) => {
      localStorage.setItem(
        'access_token',
        tokens.access_token,
      )

      localStorage.setItem(
        'refresh_token',
        tokens.refresh_token,
      )

      navigate('/viajes', {
        replace: true,
      })
    },
  })

  return (
    <Box
      component="main"
      sx={{
        minHeight: '100vh',
        overflow: 'hidden',
        bgcolor: 'background.default',
        p: {
          xs: 3,
          sm: 6,
        },
      }}
    >
      <Box
        sx={{
          opacity: isLeavingLogin ? 0 : 1,
          filter: isLeavingLogin
            ? 'blur(12px)'
            : 'blur(0)',
          transform: isLeavingLogin
            ? 'scale(0.975)'
            : 'scale(1)',
          transition:
            'opacity 260ms ease, filter 260ms ease, transform 260ms ease',
        }}
      >
        <BrandLogo />

        <Box
          sx={{
            minHeight: {
              md: 'calc(100vh - 136px)',
            },
            display: 'grid',
            placeItems: 'center',
            py: 6,
          }}
        >
          <AuthCard
            title="Bienvenido de nuevo"
            subtitle="Accede a tus viajes, reservas y planes."
          >
            <Stack
              component="form"
              spacing={3}
              onSubmit={(event) => {
                event.preventDefault()
                mutation.mutate()
              }}
            >
              {mutation.isError && (
                <Alert severity="error">
                  El correo, usuario o contraseña no son
                  correctos.
                </Alert>
              )}

              <TextField
                label="Correo electrónico o usuario"
                value={identifier}
                onChange={(event) =>
                  setIdentifier(event.target.value)
                }
                required
                autoComplete="username"
              />

              <TextField
                label="Contraseña"
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
                slotProps={{
                  htmlInput: {
                    minLength: 8,
                  },
                }}
                autoComplete="current-password"
              />

              <Button
                disabled={
                  mutation.isPending ||
                  isTransitioning
                }
                type="submit"
                variant="contained"
                size="large"
                sx={{ mt: 2 }}
              >
                {mutation.isPending
                  ? 'Iniciando sesión…'
                  : 'Iniciar sesión'}
              </Button>

              <Typography
                color="text.secondary"
                sx={{
                  textAlign: 'center',
                  fontSize: 14,
                }}
              >
                ¿No tienes cuenta?{' '}

                <Link
                  component="button"
                  type="button"
                  underline="hover"
                  onClick={() =>
                    startAuthTransition(
                      '/registro',
                      'toRegister',
                    )
                  }
                  sx={{
                    p: 0,
                    border: 0,
                    verticalAlign: 'baseline',
                    color: 'primary.main',
                    font: 'inherit',
                    fontWeight: 700,
                    cursor: isTransitioning
                      ? 'default'
                      : 'pointer',
                  }}
                >
                  Regístrate gratis
                </Link>
              </Typography>
            </Stack>
          </AuthCard>
        </Box>
      </Box>
    </Box>
  )
}