import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import { useState } from 'react'
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom'

import { getTrip, updateTrip } from '../api/trips'
import { getCurrencies } from '../api/currency'
import { DestinationsManager } from '../components/trips/DestinationsManager'
import type { TripStatus, TripUpdatePayload } from '../types/trip'

type EditTripForm = {
  name: string
  origin: string
  description: string
  startDate: string
  endDate: string
  budget: string
  currency: string
  status: TripStatus
}

const emptyForm: EditTripForm = {
  name: '',
  origin: '',
  description: '',
  startDate: '',
  endDate: '',
  budget: '0',
  currency: 'EUR',
  status: 'planning',
}

function getErrorMessage(error: unknown) {
  if (!isAxiosError(error)) return 'No se ha podido actualizar el viaje.'
  if (error.response?.status === 404) return 'El viaje ya no existe.'
  if (error.response?.status === 422) {
    return 'Revisa los datos introducidos. Algunos campos no son válidos.'
  }
  if (error.response?.status === 503) {
    return 'El servicio de monedas no está disponible. Inténtalo más tarde.'
  }
  return 'No se ha podido actualizar el viaje. Inténtalo de nuevo.'
}

export function EditTripPage() {
  const { tripId } = useParams()
  const numericTripId = Number(tripId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState<EditTripForm | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)

  const tripQuery = useQuery({
    queryKey: ['trip', numericTripId],
    queryFn: () => getTrip(numericTripId),
    enabled: Number.isInteger(numericTripId) && numericTripId > 0,
  })

  const currenciesQuery = useQuery({
    queryKey: ['currencies'],
    queryFn: getCurrencies,
    staleTime: 1000 * 60 * 60,
  })

  const displayedForm = tripQuery.data
    ? form ?? {
        name: tripQuery.data.name,
        origin: tripQuery.data.origin,
        description: tripQuery.data.description ?? '',
        startDate: tripQuery.data.start_date,
        endDate: tripQuery.data.end_date,
        budget: String(tripQuery.data.budget),
        currency: tripQuery.data.currency,
        status: tripQuery.data.status,
      }
    : emptyForm

  const mutation = useMutation({
    mutationFn: (payload: TripUpdatePayload) =>
      updateTrip(numericTripId, payload),
    onSuccess: async (updatedTrip) => {
      queryClient.setQueryData(['trip', numericTripId], updatedTrip)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['trips'] }),
        queryClient.invalidateQueries({ queryKey: ['trip-details', numericTripId] }),
      ])
      navigate(`/viajes/${updatedTrip.id}`, { replace: true })
    },
  })

  const updateField = <K extends keyof EditTripForm>(
    field: K,
    value: EditTripForm[K],
  ) =>
    setForm((current) => ({
      ...(current ?? displayedForm),
      [field]: value,
    }))

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setValidationError(null)

    if (displayedForm.endDate < displayedForm.startDate) {
      setValidationError(
        'La fecha de finalización no puede ser anterior a la fecha de inicio.',
      )
      return
    }
    if (Number(displayedForm.budget) < 0) {
      setValidationError('El presupuesto no puede ser negativo.')
      return
    }

    mutation.mutate({
      name: displayedForm.name.trim(),
      origin: displayedForm.origin.trim(),
      description: displayedForm.description.trim() || null,
      start_date: displayedForm.startDate,
      end_date: displayedForm.endDate,
      budget: Number(displayedForm.budget),
      currency: displayedForm.currency,
      status: displayedForm.status,
    })
  }

  if (!Number.isInteger(numericTripId) || numericTripId < 1) {
    return <Alert severity="error">El identificador del viaje no es válido.</Alert>
  }

  return (
    <Box
      component="main"
      sx={{
        minHeight: '100dvh',
        px: { xs: 2, sm: 4, lg: 6 },
        pt: { xs: 10, md: 5 },
        pb: 5,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 1000, mx: 'auto' }}>
        <Button
          component={RouterLink}
          to={`/viajes/${numericTripId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 1, color: 'text.secondary' }}
        >
          Volver al viaje
        </Button>

        <Typography
          component="h1"
          sx={{
            fontSize: { xs: 32, md: 38 },
            fontWeight: 800,
            letterSpacing: -0.8,
          }}
        >
          Editar viaje
        </Typography>
        <Typography sx={{ mt: 1, color: 'text.secondary', fontSize: 16 }}>
          Actualiza la información general y el estado del viaje.
        </Typography>

        {tripQuery.isLoading && (
          <Box sx={{ minHeight: 360, display: 'grid', placeItems: 'center' }}>
            <CircularProgress />
          </Box>
        )}

        {tripQuery.isError && (
          <Alert
            severity="error"
            sx={{ mt: 4 }}
            action={<Button color="inherit" onClick={() => tripQuery.refetch()}>Reintentar</Button>}
          >
            No se ha podido cargar el viaje.
          </Alert>
        )}

        {tripQuery.data && (
          <>
          <Paper
            component="form"
            variant="outlined"
            onSubmit={handleSubmit}
            sx={{
              mt: 4,
              p: { xs: 2.5, sm: 4 },
              borderRadius: '22px',
              borderColor: '#dce3ec',
            }}
          >
            {(validationError || mutation.isError) && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {validationError || getErrorMessage(mutation.error)}
              </Alert>
            )}

            <Typography component="h2" sx={{ fontSize: 21, fontWeight: 800 }}>
              Información general
            </Typography>

            <Box
              sx={{
                mt: 3,
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                gap: 2.5,
              }}
            >
              <TextField
                label="Nombre del viaje"
                value={displayedForm.name}
                onChange={(event) => updateField('name', event.target.value)}
                required
                slotProps={{ htmlInput: { maxLength: 150 } }}
              />
              <TextField
                label="Lugar de origen"
                value={displayedForm.origin}
                onChange={(event) => updateField('origin', event.target.value)}
                required
                slotProps={{ htmlInput: { maxLength: 100 } }}
              />
              <TextField
                label="Fecha de inicio"
                type="date"
                value={displayedForm.startDate}
                onChange={(event) => updateField('startDate', event.target.value)}
                required
                slotProps={{ inputLabel: { shrink: true } }}
              />
              <TextField
                label="Fecha de finalización"
                type="date"
                value={displayedForm.endDate}
                onChange={(event) => updateField('endDate', event.target.value)}
                required
                slotProps={{
                  inputLabel: { shrink: true },
                  htmlInput: { min: displayedForm.startDate || undefined },
                }}
              />
              <TextField
                label="Presupuesto"
                type="number"
                value={displayedForm.budget}
                onChange={(event) => updateField('budget', event.target.value)}
                required
                slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              />
              <TextField
                select
                label="Moneda"
                value={displayedForm.currency}
                onChange={(event) =>
                  updateField('currency', event.target.value)
                }
                required
                disabled={
                  currenciesQuery.isPending ||
                  currenciesQuery.isError
                }
                error={currenciesQuery.isError}
                helperText={
                  currenciesQuery.isPending
                    ? 'Cargando monedas...'
                    : currenciesQuery.isError
                      ? 'No se pudieron cargar las monedas.'
                      : undefined
                }
              >
                {(currenciesQuery.data ?? []).map((currency) => (
                  <MenuItem key={currency.code} value={currency.code}>
                    {currency.code} — {currency.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Estado"
                value={displayedForm.status}
                onChange={(event) =>
                  updateField('status', event.target.value as TripStatus)
                }
              >
                <MenuItem value="planning">Planificando</MenuItem>
                <MenuItem value="in_progress">En curso</MenuItem>
                <MenuItem value="completed">Completado</MenuItem>
                <MenuItem value="cancelled">Cancelado</MenuItem>
              </TextField>
              <TextField
                label="Descripción"
                value={displayedForm.description}
                onChange={(event) => updateField('description', event.target.value)}
                multiline
                minRows={4}
                sx={{ gridColumn: { md: '1 / -1' } }}
                slotProps={{ htmlInput: { maxLength: 2000 } }}
              />
            </Box>

            <Stack
              direction={{ xs: 'column-reverse', sm: 'row' }}
              spacing={2}
              sx={{ mt: 4, justifyContent: 'flex-end' }}
            >
              <Button
                component={RouterLink}
                to={`/viajes/${numericTripId}`}
                variant="outlined"
                disabled={mutation.isPending}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={
                  mutation.isPending ||
                  currenciesQuery.isPending ||
                  currenciesQuery.isError
                }
              >
                {mutation.isPending ? 'Guardando...' : 'Guardar cambios'}
              </Button>
            </Stack>
          </Paper>
          <DestinationsManager
            tripId={numericTripId}
            initialDestinations={tripQuery.data.destinations}
            currencies={currenciesQuery.data ?? []}
          />
          </>
        )}
      </Box>
    </Box>
  )
}
