import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined'
import PersonOutlineIcon from '@mui/icons-material/PersonOutlineOutlined'
import PhotoCameraOutlinedIcon from '@mui/icons-material/PhotoCameraOutlined'
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined'
import {
  Alert,
  Avatar,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { getCurrencies } from '../api/currency'
import {
  deleteCurrentUser,
  deleteCurrentUserPhoto,
  getCurrentUser,
  updateCurrentUser,
  uploadCurrentUserPhoto,
} from '../api/user'
import type { UserProfilePayload } from '../api/user'
import { UserAvatar } from '../components/UserAvatar'
import { clearStoredSession } from '../utils/authSession'

const emptyForm: UserProfilePayload = {
  name: '',
  surname: '',
  profile_photo: null,
  username: '',
  email: '',
  default_currency: 'EUR',
}

function profileToPayload(profile: UserProfilePayload): UserProfilePayload {
  return {
    name: profile.name,
    surname: profile.surname,
    profile_photo: profile.profile_photo,
    username: profile.username,
    email: profile.email,
    default_currency: profile.default_currency,
  }
}

function saveErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error)) return 'No se han podido guardar los cambios.'
  if (!error.response) return 'No se puede conectar con el servidor.'
  if (error.response.status === 401) return 'Tu sesión ha caducado. Inicia sesión de nuevo.'

  const detail = error.response.data?.detail
  if (detail === 'Email already registered') return 'Ese correo electrónico ya está registrado.'
  if (detail === 'Username already registered') return 'Ese nombre de usuario ya está registrado.'
  if (detail === 'Unsupported currency code') return 'La moneda seleccionada no está disponible.'
  if (Array.isArray(detail)) {
    return `Revisa los datos: ${detail[0]?.msg ?? 'hay un valor no válido'}.`
  }
  return 'No se han podido guardar los cambios.'
}

export function ProfilePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deleteConfirmation, setDeleteConfirmation] = useState('')
  const [form, setForm] = useState<UserProfilePayload>(emptyForm)
  const [photoValidationError, setPhotoValidationError] = useState('')
  const [selectedPhoto, setSelectedPhoto] = useState<File | null>(null)
  const [removePhoto, setRemovePhoto] = useState(false)
  const [photoPreviewUrl, setPhotoPreviewUrl] = useState<string>()

  const profileQuery = useQuery({
    queryKey: ['current-user'],
    queryFn: getCurrentUser,
  })
  const currenciesQuery = useQuery({
    queryKey: ['currencies'],
    queryFn: getCurrencies,
  })

  const saveMutation = useMutation({
    mutationFn: async ({ payload, photo, shouldRemovePhoto }: {
      payload: UserProfilePayload
      photo: File | null
      shouldRemovePhoto: boolean
    }) => {
      let updatedUser = await updateCurrentUser(payload)
      if (photo) updatedUser = await uploadCurrentUserPhoto(photo)
      else if (shouldRemovePhoto) {
        await deleteCurrentUserPhoto()
        updatedUser = { ...updatedUser, profile_photo: null }
      }
      return updatedUser
    },
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(['current-user'], updatedUser)
      queryClient.removeQueries({ queryKey: ['current-user-photo'] })
      setSelectedPhoto(null)
      setPhotoPreviewUrl(undefined)
      setRemovePhoto(false)
      setPhotoValidationError('')
      setEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCurrentUser,
    onSuccess: () => {
      clearStoredSession()
      queryClient.clear()
      navigate('/', { replace: true })
    },
  })

  const cancelEditing = () => {
    saveMutation.reset()
    setSelectedPhoto(null)
    setPhotoPreviewUrl(undefined)
    setRemovePhoto(false)
    setPhotoValidationError('')
    setEditing(false)
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    saveMutation.mutate({
      payload: {
        ...form,
        name: form.name.trim(),
        surname: form.surname.trim(),
        username: form.username.trim(),
        email: form.email.trim().toLowerCase(),
        profile_photo: form.profile_photo,
      },
      photo: selectedPhoto,
      shouldRemovePhoto: removePhoto,
    })
  }

  const handlePhoto = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    setPhotoValidationError('')
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setPhotoValidationError('Selecciona una imagen JPG o PNG.')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setPhotoValidationError('La imagen no puede superar los 5 MB.')
      return
    }
    setSelectedPhoto(file)
    setRemovePhoto(false)
    const reader = new FileReader()
    reader.onload = () => setPhotoPreviewUrl(String(reader.result))
    reader.readAsDataURL(file)
  }

  const handleLogout = () => {
    clearStoredSession()
    queryClient.clear()
    navigate('/', { replace: true })
  }

  if (profileQuery.isLoading) {
    return (
      <Box sx={{ minHeight: 360, display: 'grid', placeItems: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (profileQuery.isError || !profileQuery.data) {
    return (
      <Alert severity="error" action={<Button color="inherit" onClick={() => profileQuery.refetch()}>Reintentar</Button>}>
        No se ha podido cargar tu perfil.
      </Alert>
    )
  }

  const user = profileQuery.data

  return (
    <Box sx={{ maxWidth: 920, mx: 'auto' }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} sx={{ mb: 3, gap: 2, alignItems: { sm: 'center' }, justifyContent: 'space-between' }}>
        <Box>
          <Typography component="h1" sx={{ fontSize: { xs: 27, md: 32 }, fontWeight: 900 }}>Mi perfil</Typography>
          <Typography sx={{ mt: 0.5, color: 'text.secondary' }}>Consulta y modifica la información de tu cuenta.</Typography>
        </Box>
        {!editing && <Stack direction="row" spacing={1}>
          <Button variant="outlined" startIcon={<LogoutOutlinedIcon />} onClick={handleLogout}>Cerrar sesión</Button>
          <Button variant="contained" startIcon={<EditOutlinedIcon />} onClick={() => { setForm(profileToPayload(user)); saveMutation.reset(); setSelectedPhoto(null); setPhotoPreviewUrl(undefined); setRemovePhoto(false); setPhotoValidationError(''); setEditing(true) }}>Editar perfil</Button>
        </Stack>}
      </Stack>

      <Paper variant="outlined" sx={{ overflow: 'hidden', borderRadius: '22px', borderColor: '#dce3ec' }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2.5} sx={{ p: 3, alignItems: { sm: 'center' }, bgcolor: '#f7f9fc' }}>
          {photoPreviewUrl
            ? <Avatar src={photoPreviewUrl} sx={{ width: 86, height: 86 }} />
            : removePhoto
              ? <Avatar sx={{ width: 86, height: 86, bgcolor: 'primary.main', fontSize: 25, fontWeight: 800 }}>{`${user.name[0] ?? ''}${user.surname[0] ?? ''}`.toUpperCase()}</Avatar>
              : <UserAvatar user={user} size={86} />}
          <Box sx={{ flex: 1 }}>
            <Typography sx={{ fontSize: 22, fontWeight: 850 }}>{user.name} {user.surname}</Typography>
            <Typography sx={{ color: 'text.secondary' }}>@{user.username}</Typography>
          </Box>
          {editing && <Stack spacing={1} sx={{ alignItems: { xs: 'stretch', sm: 'flex-end' } }}>
            <Button component="label" variant="outlined" startIcon={<PhotoCameraOutlinedIcon />} disabled={saveMutation.isPending}>
              {selectedPhoto ? 'Cambiar selección' : user.profile_photo && !removePhoto ? 'Cambiar foto' : 'Añadir foto'}
              <input hidden type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" onChange={handlePhoto} />
            </Button>
            {(user.profile_photo || selectedPhoto) && !removePhoto && <Button color="error" size="small" onClick={() => { setSelectedPhoto(null); setPhotoPreviewUrl(undefined); setRemovePhoto(true) }} disabled={saveMutation.isPending}>Eliminar foto</Button>}
            {photoValidationError && <Typography color="error" sx={{ maxWidth: 260, fontSize: 12 }}>{photoValidationError}</Typography>}
            {selectedPhoto && <Typography color="text.secondary" sx={{ maxWidth: 260, fontSize: 12 }}>La foto se actualizará al guardar los cambios.</Typography>}
          </Stack>}
        </Stack>

        <Divider />

        <Box component="form" onSubmit={handleSubmit} sx={{ p: 3 }}>
          {saveMutation.isError && <Alert severity="error" sx={{ mb: 2 }}>{saveErrorMessage(saveMutation.error)}</Alert>}
          {saveMutation.isSuccess && !editing && <Alert severity="success" sx={{ mb: 2 }}>Perfil actualizado correctamente.</Alert>}

          <Stack direction="row" spacing={1} sx={{ mb: 2, alignItems: 'center' }}>
            <PersonOutlineIcon color="primary" />
            <Typography component="h2" sx={{ fontSize: 17, fontWeight: 800 }}>Datos personales</Typography>
          </Stack>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
            <TextField label="Nombre" value={editing ? form.name : user.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} disabled={!editing} required slotProps={{ htmlInput: { maxLength: 100 } }} />
            <TextField label="Apellidos" value={editing ? form.surname : user.surname} onChange={(event) => setForm((current) => ({ ...current, surname: event.target.value }))} disabled={!editing} required slotProps={{ htmlInput: { maxLength: 150 } }} />
            <TextField label="Nombre de usuario" value={editing ? form.username : user.username} onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))} disabled={!editing} required helperText={editing ? 'Letras, números, puntos, guiones y guiones bajos.' : undefined} slotProps={{ htmlInput: { minLength: 3, maxLength: 50, pattern: '[a-zA-Z0-9_.-]+' } }} />
            <TextField label="Correo electrónico" type="email" value={editing ? form.email : user.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} disabled={!editing} required />
            <TextField select label="Moneda predeterminada" value={editing ? form.default_currency : user.default_currency} onChange={(event) => setForm((current) => ({ ...current, default_currency: event.target.value }))} disabled={!editing || currenciesQuery.isPending || currenciesQuery.isError} error={editing && currenciesQuery.isError} helperText={editing && currenciesQuery.isError ? 'No se pudieron cargar las monedas.' : undefined}>
              {(editing ? form.default_currency : user.default_currency) && !(currenciesQuery.data ?? []).some((currency) => currency.code === (editing ? form.default_currency : user.default_currency)) && <MenuItem value={editing ? form.default_currency : user.default_currency}>{editing ? form.default_currency : user.default_currency}</MenuItem>}
              {(currenciesQuery.data ?? []).map((currency) => <MenuItem key={currency.code} value={currency.code}>{currency.code} — {currency.name}</MenuItem>)}
            </TextField>
          </Box>

          {editing && <Stack direction="row" spacing={1.5} sx={{ mt: 3, justifyContent: 'flex-end' }}>
            <Button onClick={cancelEditing} disabled={saveMutation.isPending}>Cancelar</Button>
            <Button type="submit" variant="contained" startIcon={<SaveOutlinedIcon />} disabled={saveMutation.isPending || currenciesQuery.isError}>{saveMutation.isPending ? 'Guardando...' : 'Guardar cambios'}</Button>
          </Stack>}
        </Box>

        {editing && <><Divider />

        <Box sx={{ p: 3 }}>
          <Typography component="h2" sx={{ color: 'error.main', fontSize: 17, fontWeight: 800 }}>Eliminar cuenta</Typography>
          <Typography sx={{ mt: 0.75, color: 'text.secondary', fontSize: 13 }}>Se eliminarán permanentemente tu perfil, todos tus viajes y sus datos asociados.</Typography>
          <Button color="error" variant="outlined" startIcon={<DeleteOutlineIcon />} onClick={() => { setDeleteConfirmation(''); deleteMutation.reset(); setDeleteOpen(true) }} sx={{ mt: 2 }}>Eliminar mi cuenta</Button>
        </Box></>}
      </Paper>

      <Dialog open={deleteOpen} onClose={() => !deleteMutation.isPending && setDeleteOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Eliminar cuenta definitivamente</DialogTitle>
        <DialogContent>
          <DialogContentText>Esta acción no se puede deshacer. Escribe <strong>{user.username}</strong> para confirmar.</DialogContentText>
          {deleteMutation.isError && <Alert severity="error" sx={{ mt: 2 }}>No se ha podido eliminar la cuenta. Inténtalo de nuevo.</Alert>}
          <TextField autoFocus fullWidth label="Nombre de usuario" value={deleteConfirmation} onChange={(event) => setDeleteConfirmation(event.target.value)} sx={{ mt: 2 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)} disabled={deleteMutation.isPending}>Cancelar</Button>
          <Button color="error" variant="contained" disabled={deleteMutation.isPending || deleteConfirmation !== user.username} onClick={() => deleteMutation.mutate()}>{deleteMutation.isPending ? 'Eliminando...' : 'Eliminar definitivamente'}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
