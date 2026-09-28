import { useEffect, useState } from 'react'
import { Alert, Box, Button, Stack, TextField, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { isAxiosError } from 'axios'

import { resendVerification, verifyEmail } from '../api/auth'
import { AuthCard } from '../components/AuthCard'

export function VerifyEmailPage() {
  const location = useLocation()
  const [email, setEmail] = useState((location.state as { email?: string } | null)?.email ?? '')
  const [token] = useState(() => new URLSearchParams(window.location.search).get('token'))
  const verification = useMutation({ mutationFn: verifyEmail })
  const resend = useMutation({ mutationFn: resendVerification })

  useEffect(() => {
    if (token) {
      window.history.replaceState(window.history.state, '', '/verificar-correo')
      verification.mutate(token)
    }
    // El enlace se verifica una sola vez al abrir la página.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  return (
    <Box component="main" sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 3 }}>
      <AuthCard title="Verifica tu correo" subtitle="Revisa tu bandeja de entrada y abre el enlace que te hemos enviado.">
        <Stack spacing={2}>
          {verification.isPending && <Typography>Verificando correo…</Typography>}
          {verification.isSuccess && <Alert severity="success">Correo verificado. Ya puedes iniciar sesión.</Alert>}
          {verification.isError && <Alert severity="error">El enlace no es válido o ha caducado. Solicita uno nuevo.</Alert>}
          {resend.isSuccess && <Alert severity="success">Si la cuenta está pendiente, enviaremos un enlace de verificación.</Alert>}
          {resend.isError && <Alert severity="error">{isAxiosError(resend.error) && typeof resend.error.response?.data?.detail === 'string' ? resend.error.response.data.detail : 'No se pudo enviar el correo. Inténtalo más tarde.'}</Alert>}
          <Box component="form" onSubmit={(event) => { event.preventDefault(); resend.mutate(email) }}>
            <Stack spacing={2}>
              <TextField type="email" label="Correo electrónico" value={email} onChange={(event) => setEmail(event.target.value)} required />
              <Button type="submit" variant="contained" disabled={resend.isPending}>Reenviar enlace</Button>
            </Stack>
          </Box>
          <Button component={RouterLink} to="/iniciar-sesion">Ir a iniciar sesión</Button>
        </Stack>
      </AuthCard>
    </Box>
  )
}
