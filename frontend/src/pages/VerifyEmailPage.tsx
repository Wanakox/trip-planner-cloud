import { useEffect, useState } from 'react'
import { Alert, Box, Button, Stack, TextField, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { isAxiosError } from 'axios'

import { changePendingEmail, resendVerification, verifyEmail } from '../api/auth'
import { AuthCard } from '../components/AuthCard'

export function VerifyEmailPage() {
  const location = useLocation()
  const [email, setEmail] = useState((location.state as { email?: string } | null)?.email ?? '')
  const [newEmail, setNewEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token] = useState(() => new URLSearchParams(window.location.search).get('token'))
  const verification = useMutation({ mutationFn: verifyEmail })
  const resend = useMutation({ mutationFn: resendVerification })
  const changeEmail = useMutation({
    mutationFn: () => changePendingEmail(email, password, newEmail),
    onSuccess: () => {
      setEmail(newEmail.trim().toLowerCase())
      setNewEmail('')
      setPassword('')
      resend.reset()
    },
  })

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
          <Box component="form" onSubmit={(event) => { event.preventDefault(); resend.reset(); resend.mutate(email) }}>
            <Stack spacing={2}>
              <TextField type="email" label="Correo usado al registrarte" value={email} onChange={(event) => { setEmail(event.target.value); resend.reset() }} required />
              <Button type="submit" variant="contained" disabled={resend.isPending || !email.trim()}>{resend.isPending ? 'Enviando…' : 'Reenviar enlace'}</Button>
            </Stack>
          </Box>
          <Typography variant="h6">¿Te equivocaste de correo?</Typography>
          <Typography variant="body2">Indica el correo usado al registrarte arriba, tu contraseña y la nueva dirección. La nueva dirección no puede pertenecer a otra cuenta.</Typography>
          {changeEmail.isSuccess && <Alert severity="success">Correo cambiado. Hemos enviado un enlace a {email}.</Alert>}
          {changeEmail.isError && <Alert severity="error">{errorMessage(changeEmail.error)}</Alert>}
          <Box component="form" onSubmit={(event) => { event.preventDefault(); changeEmail.mutate() }}>
            <Stack spacing={2}>
              <TextField label="Nuevo correo electrónico" type="email" value={newEmail} onChange={(event) => { setNewEmail(event.target.value); changeEmail.reset() }} required />
              <TextField label="Contraseña de tu cuenta" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
              <Button type="submit" disabled={changeEmail.isPending || !email.trim()}>{changeEmail.isPending ? 'Cambiando…' : 'Cambiar correo y enviar enlace'}</Button>
            </Stack>
          </Box>
          <Button component={RouterLink} to="/iniciar-sesion">Ir a iniciar sesión</Button>
        </Stack>
      </AuthCard>
    </Box>
  )
}
