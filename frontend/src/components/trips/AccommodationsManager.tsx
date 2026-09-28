import AddIcon from '@mui/icons-material/Add'
import BedOutlinedIcon from '@mui/icons-material/BedOutlined'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import {
  Alert,
  Avatar,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'

import {
  addAccommodation,
  deleteAccommodation,
  getTripAccommodations,
  updateAccommodation,
} from '../../api/trips'
import type {
  AccommodationPayload,
  TripAccommodation,
  TripDetails,
} from '../../types/trip'

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${value}T00:00:00`))
}

function emptyForm(startDate: string): AccommodationPayload {
  return {
    name: '',
    address: '',
    price: null,
    check_in_date: startDate,
    check_out_date: startDate,
    check_in_time: null,
    check_out_time: null,
  }
}

function saveErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error)) return 'No se ha podido guardar el alojamiento.'
  if (!error.response) return 'No se puede conectar con el servidor. Comprueba la conexión.'
  if (error.response.status === 401) return 'Tu sesión ha caducado. Inicia sesión de nuevo.'

  const detail = error.response.data?.detail
  if (Array.isArray(detail)) {
    return detail[0]?.msg
      ? `Hay un dato no válido: ${detail[0].msg}.`
      : 'Revisa los datos introducidos.'
  }
  if (typeof detail === 'string') {
    if (detail.includes('within the trip dates')) {
      return 'Las fechas de entrada y salida deben estar dentro de las fechas del viaje.'
    }
    if (detail.includes('chronologically valid')) {
      return 'La fecha u hora de salida no puede ser anterior a la entrada.'
    }
    return detail
  }
  return 'No se ha podido guardar el alojamiento.'
}

export function AccommodationsManager({
  tripId,
  tripStartDate,
  tripEndDate,
  currency,
  initialAccommodations,
}: {
  tripId: number
  tripStartDate: string
  tripEndDate: string
  currency: string
  initialAccommodations: TripAccommodation[]
}) {
  const queryClient = useQueryClient()
  const [accommodations, setAccommodations] = useState(initialAccommodations)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TripAccommodation | null>(null)
  const [toDelete, setToDelete] = useState<TripAccommodation | null>(null)
  const [form, setForm] = useState<AccommodationPayload>(() => emptyForm(tripStartDate))
  const [validationError, setValidationError] = useState<string | null>(null)

  const sync = (next: TripAccommodation[]) => {
    setAccommodations(next)
    queryClient.setQueryData(
      ['trip-details', tripId],
      (current: TripDetails | undefined) =>
        current ? { ...current, accommodations: next } : current,
    )
  }

  const refresh = async () => sync(await getTripAccommodations(tripId))

  const saveMutation = useMutation({
    mutationFn: (payload: AccommodationPayload) =>
      editing
        ? updateAccommodation(tripId, editing.id, payload)
        : addAccommodation(tripId, payload),
    onSuccess: async () => {
      await refresh()
      setFormOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteAccommodation(tripId, id),
    onSuccess: async () => {
      await refresh()
      setToDelete(null)
    },
  })

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm(tripStartDate))
    setValidationError(null)
    saveMutation.reset()
    setFormOpen(true)
  }

  const openEdit = (accommodation: TripAccommodation) => {
    setEditing(accommodation)
    setForm({
      name: accommodation.name,
      address: accommodation.address,
      price: accommodation.price === null ? null : Number(accommodation.price),
      check_in_date: accommodation.check_in_date,
      check_out_date: accommodation.check_out_date,
      check_in_time: accommodation.check_in_time?.slice(0, 5) ?? null,
      check_out_time: accommodation.check_out_time?.slice(0, 5) ?? null,
    })
    setValidationError(null)
    saveMutation.reset()
    setFormOpen(true)
  }

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const name = form.name.trim()
    const address = form.address.trim()
    setValidationError(null)

    if (!name || !address) {
      setValidationError('El nombre y la dirección son obligatorios.')
      return
    }
    if (
      form.check_in_date < tripStartDate ||
      form.check_out_date > tripEndDate
    ) {
      setValidationError('Las fechas deben estar dentro de las fechas del viaje.')
      return
    }
    if (form.check_out_date < form.check_in_date) {
      setValidationError('La salida no puede ser anterior a la entrada.')
      return
    }
    if (
      form.check_out_date === form.check_in_date &&
      form.check_in_time && form.check_out_time &&
      form.check_out_time < form.check_in_time
    ) {
      setValidationError('La hora de salida no puede ser anterior a la entrada.')
      return
    }

    const payload = { ...form, name, address }
    setForm(payload)
    saveMutation.mutate(payload)
  }

  return (
    <Paper variant="outlined" sx={{ p: 2.25, borderRadius: '18px', borderColor: '#dce3ec' }}>
      <Stack direction="row" sx={{ mb: 1.5, gap: 1, alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography component="h2" sx={{ fontSize: 16, fontWeight: 800 }}>Alojamiento</Typography>
        <Button size="small" startIcon={<AddIcon />} onClick={openCreate} sx={{ minHeight: 32 }}>Añadir</Button>
      </Stack>

      {deleteMutation.isError && <Alert severity="error" sx={{ mb: 2 }}>No se ha podido eliminar el alojamiento.</Alert>}

      <Stack spacing={1.5}>
        {accommodations.map((accommodation) => (
          <Stack key={accommodation.id} direction="row" spacing={1.25} sx={{ alignItems: 'flex-start' }}>
            <Avatar variant="rounded" sx={{ bgcolor: '#e2f7ef', color: 'secondary.main' }}><BedOutlinedIcon /></Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography sx={{ fontSize: 13, fontWeight: 800 }}>{accommodation.name}</Typography>
              <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>{accommodation.address}</Typography>
              <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>
                Check-in: {formatDate(accommodation.check_in_date)}
                {accommodation.check_in_time ? ` · ${accommodation.check_in_time.slice(0, 5)}` : ''}
                {' — '}Check-out: {formatDate(accommodation.check_out_date)}
                {accommodation.check_out_time ? ` · ${accommodation.check_out_time.slice(0, 5)}` : ''}
              </Typography>
              {accommodation.price !== null && (
                <Typography sx={{ mt: 0.3, color: 'text.secondary', fontSize: 12 }}>
                  {new Intl.NumberFormat('es-ES', { style: 'currency', currency }).format(Number(accommodation.price))}
                </Typography>
              )}
            </Box>
            <IconButton size="small" aria-label="Editar alojamiento" onClick={() => openEdit(accommodation)}><EditOutlinedIcon fontSize="small" /></IconButton>
            <IconButton size="small" color="error" aria-label="Eliminar alojamiento" onClick={() => { deleteMutation.reset(); setToDelete(accommodation) }}><DeleteOutlineIcon fontSize="small" /></IconButton>
          </Stack>
        ))}
        {!accommodations.length && <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>No hay alojamientos registrados.</Typography>}
      </Stack>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="md">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>{editing ? 'Editar alojamiento' : 'Añadir alojamiento'}</DialogTitle>
          <DialogContent>
            {(validationError || saveMutation.isError) && <Alert severity="error" sx={{ mb: 2 }}>{validationError || saveErrorMessage(saveMutation.error)}</Alert>}
            <Box sx={{ mt: 1, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
              <TextField label="Nombre" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required />
              <TextField label="Dirección" value={form.address} onChange={(event) => setForm((current) => ({ ...current, address: event.target.value }))} required />
              <TextField label={`Precio (${currency})`} type="number" value={form.price ?? ''} onChange={(event) => setForm((current) => ({ ...current, price: event.target.value === '' ? null : Number(event.target.value) }))} slotProps={{ htmlInput: { min: 0, step: 0.01 } }} />
              <Box />
              <TextField label="Fecha de check-in" type="date" value={form.check_in_date} onChange={(event) => setForm((current) => ({ ...current, check_in_date: event.target.value }))} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: tripStartDate, max: tripEndDate } }} />
              <TextField label="Hora de check-in" type="time" value={form.check_in_time ?? ''} onChange={(event) => setForm((current) => ({ ...current, check_in_time: event.target.value || null }))} slotProps={{ inputLabel: { shrink: true } }} />
              <TextField label="Fecha de check-out" type="date" value={form.check_out_date} onChange={(event) => setForm((current) => ({ ...current, check_out_date: event.target.value }))} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: form.check_in_date, max: tripEndDate } }} />
              <TextField label="Hora de check-out" type="time" value={form.check_out_time ?? ''} onChange={(event) => setForm((current) => ({ ...current, check_out_time: event.target.value || null }))} slotProps={{ inputLabel: { shrink: true } }} />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={saveMutation.isPending}>{saveMutation.isPending ? 'Guardando...' : 'Guardar alojamiento'}</Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(toDelete)} onClose={() => !deleteMutation.isPending && setToDelete(null)} fullWidth maxWidth="xs">
        <DialogTitle>Eliminar alojamiento</DialogTitle>
        <DialogContent><DialogContentText>¿Quieres eliminar «{toDelete?.name}»?</DialogContentText></DialogContent>
        <DialogActions>
          <Button onClick={() => setToDelete(null)} disabled={deleteMutation.isPending}>Cancelar</Button>
          <Button color="error" variant="contained" disabled={deleteMutation.isPending} onClick={() => { if (toDelete) deleteMutation.mutate(toDelete.id) }}>{deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}
