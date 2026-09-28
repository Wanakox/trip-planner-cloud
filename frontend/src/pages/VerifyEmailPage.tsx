import { useEffect, useState } from 'react'
import { Alert, Box, Button, Stack, TextField, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'
import { isAxiosError } from 'axios'

import { changePendingEmail, resendVerification, verifyEmail } from '../api/auth'
import { AuthCard } from '../components/AuthCard'
import { BrandLogo } from '../components/BrandLogo'

export function VerifyEmailPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const initialState = location.state as { email?: string; identifier?: string } | null
  const [email, setEmail] = useState(initialState?.email ?? sessionStorage.getItem('pending_email') ?? '')
  const [newEmail, setNewEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token] = useState(() => new URLSearchParams(window.location.search).get('token'))
  const verification = useMutation({ mutationFn: verifyEmail })
  const [secondsRemaining, setSecondsRemaining] = useState(0)
  const resend = useMutation({
    mutationFn: () => resendVerification(email),
    onSuccess: () => setSecondsRemaining(20),
  })
  const changeEmail = useMutation({
    mutationFn: () => changePendingEmail(email, password, newEmail),
    onSuccess: () => {
      setEmail(newEmail.trim().toLowerCase())
      sessionStorage.setItem('pending_email', newEmail.trim().toLowerCase())
      setNewEmail('')
      setPassword('')
      setSecondsRemaining(20)
    },
  })

  useEffect(() => {
    if (email) sessionStorage.setItem('pending_email', email)
  }, [email])

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
      verification.mutate(token, {
        onSuccess: () => {
          sessionStorage.removeItem('pending_email')
          navigate('/iniciar-sesion', { replace: true, state: { emailVerified: true } })
        },
      })
    }
    // El enlace se verifica una sola vez al abrir la página.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  return (
    <Box component="main" sx={{ minHeight: '100vh', p: 3 }}>
      <BrandLogo />
      <Box sx={{ minHeight: 'calc(100vh - 90px)', display: 'grid', placeItems: 'center' }}>
      <AuthCard title="Verifica tu correo" subtitle="Revisa tu bandeja de entrada y abre el enlace que te hemos enviado.">
        <Stack spacing={2}>
          {verification.isPending && <Typography>Verificando correo…</Typography>}
          {verification.isSuccess && <Alert severity="success">Correo verificado. Ya puedes iniciar sesión.</Alert>}
          {verification.isError && <Alert severity="error">{errorMessage(verification.error)}</Alert>}
          {resend.isSuccess && <Alert severity="success">Hemos enviado el enlace. Revisa también Spam.</Alert>}
          {resend.isError && <Alert severity="error">{errorMessage(resend.error)}</Alert>}
          {changeEmail.isSuccess && <Alert severity="success">Hemos enviado el enlace a {email}.</Alert>}
          {changeEmail.isError && <Alert severity="error">{errorMessage(changeEmail.error)}</Alert>}
          <Typography variant="body2">Correo usado al registrarse: <strong>{email || 'No disponible'}</strong></Typography>
          <Box component="form" onSubmit={(event) => { event.preventDefault(); resend.reset(); resend.mutate() }}>
            <Stack spacing={2}>
              <Button type="submit" variant="contained" disabled={resend.isPending || secondsRemaining > 0 || !email}>{resend.isPending ? 'Enviando…' : secondsRemaining ? `Reenviar en ${secondsRemaining} s` : 'Reenviar enlace'}</Button>
            </Stack>
          </Box>
          <Typography variant="body2">¿Necesitas enviarlo a otro correo? Confirma tu contraseña. El nuevo correo pasará a ser el de tu cuenta.</Typography>
          <Box component="form" onSubmit={(event) => { event.preventDefault(); changeEmail.reset(); changeEmail.mutate() }}>
            <Stack spacing={2}>
              <TextField type="email" label="Nuevo correo" value={newEmail} onChange={(event) => setNewEmail(event.target.value)} required />
              <TextField type="password" label="Contraseña" value={password} onChange={(event) => setPassword(event.target.value)} required />
              <Button type="submit" disabled={changeEmail.isPending || secondsRemaining > 0 || !email}>{changeEmail.isPending ? 'Enviando…' : secondsRemaining ? `Enviar en ${secondsRemaining} s` : 'Enviar al nuevo correo'}</Button>
            </Stack>
          </Box>
          <Button component={RouterLink} to="/iniciar-sesion">Ir a iniciar sesión</Button>
        </Stack>
      </AuthCard>
      </Box>
    </Box>
  )
}
