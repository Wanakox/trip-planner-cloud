import { useEffect, useState } from 'react'
import { Alert, Box, Button, Stack, TextField, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { isAxiosError } from 'axios'

import { resendVerification, verifyEmail } from '../api/auth'
import { AuthCard } from '../components/AuthCard'

export function VerifyEmailPage() {
  const location = useLocation()
  const initialState = location.state as { email?: string; identifier?: string } | null
  const [email, setEmail] = useState(initialState?.email ?? '')
  const [identifier, setIdentifier] = useState(initialState?.identifier ?? '')
  const [password, setPassword] = useState('')
  const [token] = useState(() => new URLSearchParams(window.location.search).get('token'))
  const verification = useMutation({ mutationFn: verifyEmail })
  const [secondsRemaining, setSecondsRemaining] = useState(0)
  const resend = useMutation({
    mutationFn: () => resendVerification(identifier, password, email),
    onSuccess: ({ username }) => {
      setIdentifier(username)
      setPassword('')
      setSecondsRemaining(20)
    },
  })

  useEffect(() => {
    if (!secondsRemaining) return
    const timer = window.setTimeout(() => setSecondsRemaining(secondsRemaining - 1), 1000)
    return () => window.clearTimeout(timer)
  }, [secondsRemaining])

  function errorMessage(error: unknown): string {
    if (isAxiosError(error) && typeof error.response?.data?.detail === 'string') {
      return error.response.data.detail
    }
    return 'No se pudo completar la solicitud. Inténtalo más tarde.'
  }

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
          {verification.isError && <Alert severity="error">{errorMessage(verification.error)}</Alert>}
          {resend.isSuccess && <Alert severity="success">Hemos enviado el enlace. Revisa también Spam.</Alert>}
          {resend.isError && <Alert severity="error">{errorMessage(resend.error)}</Alert>}
          <Typography variant="body2">Puedes enviarlo a otra dirección. Por seguridad, confirma tu nombre de usuario y contraseña. Al verificar el enlace, la cuenta usará el correo de destino.</Typography>
          <Box component="form" onSubmit={(event) => { event.preventDefault(); resend.reset(); resend.mutate() }}>
            <Stack spacing={2}>
              <TextField label="Nombre de usuario" value={identifier} onChange={(event) => setIdentifier(event.target.value)} required />
              <TextField type="email" label="Correo donde recibir el enlace" value={email} onChange={(event) => { setEmail(event.target.value); resend.reset() }} required />
              <TextField type="password" label="Contraseña de la cuenta" value={password} onChange={(event) => setPassword(event.target.value)} required />
              <Button type="submit" variant="contained" disabled={resend.isPending || secondsRemaining > 0 || !identifier.trim()}>{resend.isPending ? 'Enviando…' : secondsRemaining ? `Reenviar en ${secondsRemaining} s` : 'Enviar enlace'}</Button>
            </Stack>
          </Box>
          <Button component={RouterLink} to="/iniciar-sesion">Ir a iniciar sesión</Button>
        </Stack>
      </AuthCard>
    </Box>
  )
}
