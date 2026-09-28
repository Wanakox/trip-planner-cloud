import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import {
  Alert,
  Box,
  Button,
  Link,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import { useNavigate } from 'react-router-dom'

import { useAuthTransition } from '../components/AuthTransition'
import { registerUser } from '../api/auth'
import { getCurrencies } from '../api/currency'
import { AuthCard } from '../components/AuthCard'
import { BrandLogo } from '../components/BrandLogo'

const initialForm = {
  name: '',
  surname: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  defaultCurrency: 'EUR',
}

const registerErrorFallback =
  'No se ha podido crear la cuenta. Revisa los datos o inténtalo de nuevo.'

function getRegisterErrorMessage(error: unknown) {
  if (!isAxiosError(error)) {
    return registerErrorFallback
  }

  const responseData = error.response?.data

  if (
    typeof responseData === 'object' &&
    responseData !== null &&
    'detail' in responseData &&
    typeof responseData.detail === 'string'
  ) {
    return responseData.detail
  }

  return registerErrorFallback
}

export function RegisterPage() {
  const navigate = useNavigate()
  const {
    phase,
    direction,
    isTransitioning,
    startAuthTransition,
  } = useAuthTransition()

  const isLeavingRegister =
    direction === 'toLogin' &&
    (phase === 'fade' || phase === 'cover')

  const [form, setForm] = useState(initialForm)
  const [formError, setFormError] = useState('')

  const currenciesQuery = useQuery({
    queryKey: ['currencies'],
    queryFn: getCurrencies,
    staleTime: 1000 * 60 * 60,
  })

  const update =
    (field: keyof typeof form) =>
      (event: ChangeEvent<HTMLInputElement>) => {
        setForm((current) => ({
          ...current,
          [field]: event.target.value,
        }))
      }

  const mutation = useMutation({
    mutationFn: () =>
      registerUser({
        name: form.name,
        surname: form.surname,
        username: form.username,
        email: form.email,
        password: form.password,
        default_currency: form.defaultCurrency,
      }),
    onSuccess: () => navigate('/iniciar-sesion'),
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()

    if (form.password !== form.confirmPassword) {
      setFormError('Las contraseñas no coinciden.')
      return
    }

    setFormError('')
    mutation.mutate()
  }

  return (
    <Box
      component="main"
      sx={{
        position: 'relative',
        minHeight: '100vh',
        overflow: 'hidden',
        bgcolor: 'background.default',
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          md: '41% 59%',
        },
      }}
    >
      {/* Panel azul */}
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          overflow: 'hidden',
          color: 'white',
          p: {
            xs: 4,
            sm: 7,
          },
          display: {
            xs: 'none',
            md: 'block',
          },
          background:
            'linear-gradient(145deg, #1557c8 0%, #2168d7 55%, #2d74e3 100%)',
        }}
      >
        {/* Decoración del fondo */}
        <Box
          sx={{
            position: 'absolute',
            width: 310,
            height: 310,
            borderRadius: '50%',
            bgcolor: 'rgba(255,255,255,0.04)',
            top: -150,
            right: -120,
          }}
        />

        <Box
          sx={{
            position: 'absolute',
            width: 230,
            height: 230,
            borderRadius: '50%',
            border: '1px solid rgba(255,255,255,0.07)',
            bottom: -90,
            left: -80,
          }}
        />

        <Box
          sx={{
            position: 'relative',
            opacity: isLeavingRegister ? 0 : 1,
            filter: isLeavingRegister
              ? 'blur(12px)'
              : 'blur(0)',
            transform: isLeavingRegister
              ? 'scale(0.975)'
              : 'scale(1)',
            transition:
              'opacity 260ms ease, filter 260ms ease, transform 260ms ease',
          }}
        >
          <BrandLogo inverse />

          <Typography
            component="h1"
            sx={{
              mt: 10,
              maxWidth: 470,
              fontSize: {
                md: 38,
                lg: 42,
              },
              lineHeight: 1.2,
              fontWeight: 800,
              letterSpacing: -0.7,
            }}
          >
            Empieza con tu primer viaje. Más fácil que nunca.
          </Typography>

          <Typography
            sx={{
              mt: 2,
              maxWidth: 440,
              color: '#dbecff',
              fontSize: 17,
              lineHeight: 1.65,
            }}
          >
            Reúne itinerario, presupuesto y reservas en un espacio
            diseñado para disfrutar más y preocuparte menos.
          </Typography>

          {/* Tarjeta del viaje */}
          <Paper
            elevation={0}
            sx={{
              mt: 5,
              maxWidth: 475,
              overflow: 'hidden',
              borderRadius: '22px',
              bgcolor: 'white',
              boxShadow: '0 22px 50px rgba(8, 39, 95, 0.22)',
              transition: 'transform 200ms ease, box-shadow 200ms ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 28px 60px rgba(8, 39, 95, 0.28)',
              },
            }}
          >
            {/* Cabecera de la tarjeta */}
            <Box
              sx={{
                position: 'relative',
                overflow: 'hidden',
                px: 3,
                py: 2.4,
                color: 'white',
                background:
                  'linear-gradient(135deg, #1f4fd1 0%, #3267e8 58%, #5688f4 100%)',
              }}
            >
              <Box
                sx={{
                  position: 'absolute',
                  width: 125,
                  height: 125,
                  borderRadius: '50%',
                  bgcolor: 'rgba(255,255,255,0.09)',
                  top: -65,
                  right: -20,
                }}
              />

              <Box
                sx={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 0.8,
                    bgcolor: 'rgba(255,255,255,0.96)',
                    color: '#1f5ed3',
                    borderRadius: '999px',
                    px: 1.5,
                    py: 0.6,
                    fontSize: 12,
                    fontWeight: 800,
                    boxShadow: '0 3px 10px rgba(15,23,42,0.12)',
                  }}
                >
                  <Box
                    sx={{
                      width: 7,
                      height: 7,
                      borderRadius: '50%',
                      bgcolor: '#2d63db',
                    }}
                  />

                  Planificando
                </Box>

                <Typography
                  sx={{
                    color: 'rgba(255,255,255,0.82)',
                    fontSize: 12,
                    fontWeight: 700,
                  }}
                >
                  7 días
                </Typography>
              </Box>

              <Typography
                component="h2"
                sx={{
                  position: 'relative',
                  mt: 1.4,
                  color: 'white',
                  fontSize: 25,
                  lineHeight: 1.15,
                  fontWeight: 800,
                  letterSpacing: -0.4,
                }}
              >
                Aventura por Creta
              </Typography>

              <Typography
                sx={{
                  position: 'relative',
                  mt: 0.5,
                  color: 'rgba(255,255,255,0.78)',
                  fontSize: 13,
                }}
              >
                Tu próxima aventura por el Mediterráneo
              </Typography>
            </Box>

            {/* Información del viaje */}
            <Box sx={{ px: 3, py: 2.4 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1.2,
                }}
              >
                <Box
                  sx={{
                    flexShrink: 0,
                    width: 34,
                    height: 34,
                    display: 'grid',
                    placeItems: 'center',
                    borderRadius: '10px',
                    bgcolor: '#eaf2ff',
                    color: '#1f5ed3',
                    fontSize: 16,
                  }}
                >
                  ◈
                </Box>

                <Box>
                  <Typography
                    color="text.secondary"
                    sx={{
                      fontSize: 10,
                      fontWeight: 800,
                      letterSpacing: 0.7,
                    }}
                  >
                    DESTINOS
                  </Typography>

                  <Typography
                    sx={{
                      mt: 0.25,
                      color: 'text.primary',
                      fontSize: 14,
                      fontWeight: 600,
                    }}
                  >
                    Heraclión · Matalá · Chania, Grecia
                  </Typography>
                </Box>
              </Box>

              <Box
                sx={{
                  mt: 1.7,
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 1.2,
                }}
              >
                <Box
                  sx={{
                    bgcolor: '#f6f8fc',
                    border: '1px solid #e6ebf2',
                    borderRadius: '12px',
                    px: 1.5,
                    py: 1.1,
                  }}
                >
                  <Typography
                    color="text.secondary"
                    sx={{
                      fontSize: 9,
                      fontWeight: 800,
                      letterSpacing: 0.6,
                    }}
                  >
                    FECHAS
                  </Typography>

                  <Typography
                    sx={{
                      mt: 0.35,
                      fontSize: 13,
                      fontWeight: 700,
                    }}
                  >
                    12–19 SEP 2026
                  </Typography>
                </Box>

                <Box
                  sx={{
                    bgcolor: '#f6f8fc',
                    border: '1px solid #e6ebf2',
                    borderRadius: '12px',
                    px: 1.5,
                    py: 1.1,
                  }}
                >
                  <Typography
                    color="text.secondary"
                    sx={{
                      fontSize: 9,
                      fontWeight: 800,
                      letterSpacing: 0.6,
                    }}
                  >
                    PRESUPUESTO
                  </Typography>

                  <Typography
                    sx={{
                      mt: 0.35,
                      color: '#1f5ed3',
                      fontSize: 15,
                      fontWeight: 800,
                    }}
                  >
                    1.350 €
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>

      {/* Formulario */}
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          p: {
            xs: 3,
            sm: 5,
          },
          display: 'grid',
          placeItems: 'center',
        }}
      >
        <Box
          sx={{
            display: {
              xs: 'block',
              md: 'none',
            },
            justifySelf: 'start',
            width: '100%',
            mb: 3,
          }}
        >
          <BrandLogo />
        </Box>

        <AuthCard
          title="Crea tu cuenta"
          subtitle="Empieza a organizar tu próximo viaje en minutos."
        >
          <Stack
            component="form"
            spacing={2.2}
            onSubmit={submit}
          >
            {(formError || mutation.isError) && (
              <Alert severity="error">
                {formError ||
                  getRegisterErrorMessage(mutation.error)}
              </Alert>
            )}

            <TextField
              label="Nombre"
              value={form.name}
              onChange={update('name')}
              required
              autoComplete="given-name"
            />

            <TextField
              label="Apellido"
              value={form.surname}
              onChange={update('surname')}
              required
              autoComplete="family-name"
            />

            <TextField
              label="Nombre de usuario"
              value={form.username}
              onChange={update('username')}
              required
              slotProps={{
                htmlInput: {
                  minLength: 3,
                  pattern: '[a-zA-Z0-9_.-]+',
                },
              }}
              autoComplete="username"
            />

            <TextField
              label="Correo electrónico"
              type="email"
              value={form.email}
              onChange={update('email')}
              required
              autoComplete="email"
            />

            <TextField
              label="Contraseña"
              type="password"
              value={form.password}
              onChange={update('password')}
              required
              slotProps={{
                htmlInput: {
                  minLength: 8,
                },
              }}
              autoComplete="new-password"
            />

            <TextField
              label="Confirmar contraseña"
              type="password"
              value={form.confirmPassword}
              onChange={update('confirmPassword')}
              required
              slotProps={{
                htmlInput: {
                  minLength: 8,
                },
              }}
              autoComplete="new-password"
            />

            <TextField
              select
              label="Moneda predeterminada"
              value={form.defaultCurrency}
              onChange={update('defaultCurrency')}
              disabled={
                currenciesQuery.isPending || currenciesQuery.isError
              }
              helperText={
                currenciesQuery.isPending
                  ? 'Cargando monedas…'
                  : currenciesQuery.isError
                    ? 'No se pudieron cargar las monedas.'
                    : undefined
              }
              error={currenciesQuery.isError}
            >
              {(currenciesQuery.data ?? []).map((currency) => (
                <MenuItem
                  key={currency.code}
                  value={currency.code}
                >
                  {currency.code} — {currency.name}
                </MenuItem>
              ))}
            </TextField>

            <Button
              disabled={
                mutation.isPending ||
                isTransitioning ||
                !currenciesQuery.isSuccess
              }
              type="submit"
              variant="contained"
              size="large"
            >
              {mutation.isPending
                ? 'Creando cuenta…'
                : 'Crear cuenta'}
            </Button>

            <Typography
              color="text.secondary"
              sx={{
                textAlign: 'center',
                fontSize: 14,
              }}
            >
              ¿Ya tienes una cuenta?{' '}

              <Link
                component="button"
                type="button"
                underline="hover"
                onClick={() =>
                  startAuthTransition(
                    '/iniciar-sesion',
                    'toLogin',
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
                Inicia sesión
              </Link>
            </Typography>
          </Stack>
        </AuthCard>
      </Box>
    </Box>
  )
}
