import AddIcon from '@mui/icons-material/Add'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import DirectionsBoatOutlinedIcon from '@mui/icons-material/DirectionsBoatOutlined'
import DirectionsBusOutlinedIcon from '@mui/icons-material/DirectionsBusOutlined'
import DirectionsCarOutlinedIcon from '@mui/icons-material/DirectionsCarOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import FlightOutlinedIcon from '@mui/icons-material/FlightOutlined'
import TrainOutlinedIcon from '@mui/icons-material/TrainOutlined'
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
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'

import {
  addTransport,
  deleteTransport,
  getTripTransports,
  updateTransport,
} from '../../api/trips'
import type {
  TransportPayload,
  TripDetails,
  TripTransport,
} from '../../types/trip'

const transportLabels: Record<TripTransport['transport_type'], string> = {
  flight: 'Vuelo',
  train: 'Tren',
  bus: 'Autobús',
  car: 'Coche',
  boat: 'Barco',
  other: 'Otro',
}

function TransportIcon({ type }: { type: TripTransport['transport_type'] }) {
  if (type === 'flight') return <FlightOutlinedIcon />
  if (type === 'train') return <TrainOutlinedIcon />
  if (type === 'boat') return <DirectionsBoatOutlinedIcon />
  if (type === 'car') return <DirectionsCarOutlinedIcon />
  return <DirectionsBusOutlinedIcon />
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${value}T00:00:00`))
}

function createEmptyForm(startDate: string): TransportPayload {
  return {
    transport_type: 'flight',
    price: null,
    departure_date: startDate,
    arrival_date: startDate,
    departure_time: null,
    arrival_time: null,
    origin: '',
    destination: '',
    check_in_date: null,
  }
}

type ApiErrorDetail = {
  loc?: Array<string | number>
  msg?: string
}

const fieldLabels: Record<string, string> = {
  transport_type: 'tipo',
  price: 'precio',
  departure_date: 'fecha de salida',
  arrival_date: 'fecha de llegada',
  departure_time: 'hora de salida',
  arrival_time: 'hora de llegada',
  origin: 'origen',
  destination: 'destino',
  check_in_date: 'fecha de check-in',
}

function getSaveErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'No se ha podido guardar el transporte. Inténtalo de nuevo.'
  }

  if (!error.response) {
    return 'No se puede conectar con el servidor. Comprueba la conexión e inténtalo de nuevo.'
  }

  if (error.response.status === 401) {
    return 'Tu sesión ha caducado. Inicia sesión de nuevo para guardar el transporte.'
  }

  const detail = error.response.data?.detail

  if (Array.isArray(detail)) {
    const firstError = detail[0] as ApiErrorDetail | undefined
    const field = firstError?.loc?.at(-1)
    const label = typeof field === 'string' ? fieldLabels[field] : null

    return label
      ? `Revisa el campo «${label}»: ${firstError?.msg ?? 'el valor no es válido'}.`
      : 'Hay datos no válidos en el formulario. Revisa los campos e inténtalo de nuevo.'
  }

  if (typeof detail === 'string') {
    if (detail.includes('within the trip dates')) {
      return 'Las fechas de salida y llegada deben estar dentro de las fechas del viaje.'
    }
    if (detail.includes('chronologically valid')) {
      return 'Las fechas u horas no siguen un orden cronológico válido.'
    }
    if (detail === 'Trip not found') {
      return 'El viaje ya no existe o no pertenece a tu cuenta.'
    }

    return detail
  }

  return 'No se ha podido guardar el transporte. Inténtalo de nuevo.'
}

export function TransportsManager({
  tripId,
  tripStartDate,
  tripEndDate,
  currency,
  initialTransports,
}: {
  tripId: number
  tripStartDate: string
  tripEndDate: string
  currency: string
  initialTransports: TripTransport[]
}) {
  const queryClient = useQueryClient()
  const [transports, setTransports] = useState(initialTransports)
  const [formOpen, setFormOpen] = useState(false)
  const [editingTransport, setEditingTransport] = useState<TripTransport | null>(null)
  const [transportToDelete, setTransportToDelete] = useState<TripTransport | null>(null)
  const [form, setForm] = useState<TransportPayload>(() =>
    createEmptyForm(tripStartDate),
  )
  const [validationError, setValidationError] = useState<string | null>(null)

  const syncTransports = (nextTransports: TripTransport[]) => {
    setTransports(nextTransports)
    queryClient.setQueryData(
      ['trip-details', tripId],
      (current: TripDetails | undefined) =>
        current ? { ...current, transports: nextTransports } : current,
    )
  }

  const refreshTransports = async () => {
    syncTransports(await getTripTransports(tripId))
  }

  const saveMutation = useMutation({
    mutationFn: (payload: TransportPayload) =>
      editingTransport
        ? updateTransport(tripId, editingTransport.id, payload)
        : addTransport(tripId, payload),
    onSuccess: async () => {
      await refreshTransports()
      setFormOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (transportId: number) => deleteTransport(tripId, transportId),
    onSuccess: async () => {
      await refreshTransports()
      setTransportToDelete(null)
    },
  })

  const openCreate = () => {
    setEditingTransport(null)
    setForm(createEmptyForm(tripStartDate))
    setValidationError(null)
    saveMutation.reset()
    setFormOpen(true)
  }

  const openEdit = (transport: TripTransport) => {
    setEditingTransport(transport)
    setForm({
      transport_type: transport.transport_type,
      price: transport.price === null ? null : Number(transport.price),
      departure_date: transport.departure_date,
      arrival_date: transport.arrival_date,
      departure_time: transport.departure_time?.slice(0, 5) ?? null,
      arrival_time: transport.arrival_time?.slice(0, 5) ?? null,
      origin: transport.origin,
      destination: transport.destination,
      check_in_date: transport.check_in_date,
    })
    setValidationError(null)
    saveMutation.reset()
    setFormOpen(true)
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setValidationError(null)

    const origin = form.origin.trim()
    const destination = form.destination.trim()

    if (!origin || !destination) {
      setValidationError('El origen y el destino son obligatorios.')
      return
    }

    if (
      form.departure_date < tripStartDate ||
      form.departure_date > tripEndDate ||
      (form.arrival_date &&
        (form.arrival_date < tripStartDate || form.arrival_date > tripEndDate))
    ) {
      setValidationError('Las fechas de salida y llegada deben estar dentro de las fechas del viaje.')
      return
    }

    if (form.arrival_date && form.arrival_date < form.departure_date) {
      setValidationError('La llegada no puede ser anterior a la salida.')
      return
    }
    if (
      form.arrival_date === form.departure_date &&
      form.departure_time &&
      form.arrival_time &&
      form.arrival_time < form.departure_time
    ) {
      setValidationError('La hora de llegada no puede ser anterior a la salida.')
      return
    }
    if (form.check_in_date && form.check_in_date > form.departure_date) {
      setValidationError('El check-in no puede ser posterior a la salida.')
      return
    }

    setForm((current) => ({ ...current, origin, destination }))
    saveMutation.mutate({ ...form, origin, destination })
  }

  return (
    <Paper variant="outlined" sx={{ p: 2.25, borderRadius: '18px', borderColor: '#dce3ec' }}>
      <Stack direction="row" sx={{ mb: 1.5, gap: 1, alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography component="h2" sx={{ fontSize: 16, fontWeight: 800 }}>
          Transporte
        </Typography>
        <Button size="small" startIcon={<AddIcon />} onClick={openCreate} sx={{ minHeight: 32 }}>
          Añadir
        </Button>
      </Stack>

      {deleteMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>No se ha podido eliminar el transporte.</Alert>
      )}

      <Stack spacing={1.5}>
        {transports.map((transport) => (
          <Stack key={transport.id} direction="row" spacing={1.25} sx={{ alignItems: 'flex-start' }}>
            <Avatar variant="rounded" sx={{ bgcolor: 'primary.light', color: 'primary.main' }}>
              <TransportIcon type={transport.transport_type} />
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography sx={{ fontSize: 13, fontWeight: 800 }}>
                {transportLabels[transport.transport_type]} · {transport.origin} → {transport.destination}
              </Typography>
              <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>
                {formatDate(transport.departure_date)}
                {transport.departure_time ? ` · ${transport.departure_time.slice(0, 5)}` : ''}
                {transport.arrival_date ? ` — ${formatDate(transport.arrival_date)}` : ''}
                {transport.arrival_time ? ` · ${transport.arrival_time.slice(0, 5)}` : ''}
              </Typography>
              {transport.check_in_date && (
                <Typography sx={{ mt: 0.3, color: 'text.secondary', fontSize: 12 }}>
                  Check-in: {formatDate(transport.check_in_date)}
                </Typography>
              )}
              {transport.price !== null && (
                <Typography sx={{ mt: 0.3, color: 'text.secondary', fontSize: 12 }}>
                  {new Intl.NumberFormat('es-ES', { style: 'currency', currency }).format(Number(transport.price))}
                </Typography>
              )}
            </Box>
            <IconButton size="small" aria-label="Editar transporte" onClick={() => openEdit(transport)}>
              <EditOutlinedIcon fontSize="small" />
            </IconButton>
            <IconButton
              size="small"
              color="error"
              aria-label="Eliminar transporte"
              onClick={() => {
                deleteMutation.reset()
                setTransportToDelete(transport)
              }}
            >
              <DeleteOutlineIcon fontSize="small" />
            </IconButton>
          </Stack>
        ))}
        {!transports.length && (
          <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>
            No hay transportes registrados.
          </Typography>
        )}
      </Stack>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="md">
        <Box component="form" onSubmit={handleSubmit}>
          <DialogTitle>{editingTransport ? 'Editar transporte' : 'Añadir transporte'}</DialogTitle>
          <DialogContent>
            {(validationError || saveMutation.isError) && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {validationError || getSaveErrorMessage(saveMutation.error)}
              </Alert>
            )}
            <Box sx={{ mt: 1, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
              <TextField
                select
                label="Tipo"
                value={form.transport_type}
                onChange={(event) => setForm((current) => ({ ...current, transport_type: event.target.value as TripTransport['transport_type'] }))}
              >
                {Object.entries(transportLabels).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
              <TextField
                label={`Precio (${currency})`}
                type="number"
                value={form.price ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, price: event.target.value === '' ? null : Number(event.target.value) }))}
                slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              />
              <TextField label="Origen" value={form.origin} onChange={(event) => setForm((current) => ({ ...current, origin: event.target.value }))} required />
              <TextField label="Destino" value={form.destination} onChange={(event) => setForm((current) => ({ ...current, destination: event.target.value }))} required />
              <TextField
                label="Fecha de salida"
                type="date"
                value={form.departure_date}
                onChange={(event) => setForm((current) => ({ ...current, departure_date: event.target.value }))}
                required
                slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: tripStartDate, max: tripEndDate } }}
              />
              <TextField
                label="Hora de salida"
                type="time"
                value={form.departure_time ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, departure_time: event.target.value || null }))}
                slotProps={{ inputLabel: { shrink: true } }}
              />
              <TextField
                label="Fecha de llegada"
                type="date"
                value={form.arrival_date ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, arrival_date: event.target.value || null }))}
                slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: form.departure_date, max: tripEndDate } }}
              />
              <TextField
                label="Hora de llegada"
                type="time"
                value={form.arrival_time ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, arrival_time: event.target.value || null }))}
                slotProps={{ inputLabel: { shrink: true } }}
              />
              <TextField
                label="Fecha de check-in"
                type="date"
                value={form.check_in_date ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, check_in_date: event.target.value || null }))}
                slotProps={{ inputLabel: { shrink: true }, htmlInput: { max: form.departure_date } }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Guardando...' : 'Guardar transporte'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(transportToDelete)} onClose={() => !deleteMutation.isPending && setTransportToDelete(null)} fullWidth maxWidth="xs">
        <DialogTitle>Eliminar transporte</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Quieres eliminar el trayecto de {transportToDelete?.origin} a {transportToDelete?.destination}?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTransportToDelete(null)} disabled={deleteMutation.isPending}>Cancelar</Button>
          <Button
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (transportToDelete) deleteMutation.mutate(transportToDelete.id)
            }}
          >
            {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}
