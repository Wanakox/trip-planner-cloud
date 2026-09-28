import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import DownloadIcon from '@mui/icons-material/Download'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import StarOutlineIcon from '@mui/icons-material/StarOutlined'
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Rating,
  Stack,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom'

import {
  deleteTrip,
  downloadTripExport,
  getTripDetails,
  rateTrip,
} from '../api/trips'
import { ActivitiesManager } from '../components/trips/ActivitiesManager'
import { AccommodationsManager } from '../components/trips/AccommodationsManager'
import { TransportsManager } from '../components/trips/TransportsManager'
import { ChecklistManager } from '../components/trips/ChecklistManager'
import { ParticipantsManager } from '../components/trips/ParticipantsManager'
import { ExpensesManager } from '../components/trips/ExpensesManager'
import { NotesManager } from '../components/trips/NotesManager'
import { DocumentsManager } from '../components/trips/DocumentsManager'
import { CurrencyConverter } from '../components/trips/CurrencyConverter'
import type { TripStatus } from '../types/trip'

const statusConfig: Record<
  TripStatus,
  { label: string; color: 'primary' | 'warning' | 'success' | 'error' }
> = {
  planning: { label: 'Planificando', color: 'primary' },
  in_progress: { label: 'En curso', color: 'warning' },
  completed: { label: 'Completado', color: 'success' },
  cancelled: { label: 'Cancelado', color: 'error' },
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${value}T00:00:00`))
}

export function TripDetailsPage() {
  const { tripId } = useParams()
  const numericTripId = Number(tripId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState(false)
  const [ratingOpen, setRatingOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedRating, setSelectedRating] = useState<number | null>(null)
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['trip-details', numericTripId],
    queryFn: () => getTripDetails(numericTripId),
    enabled: Number.isInteger(numericTripId) && numericTripId > 0,
  })
  const usedCurrencies = data
    ? Array.from(new Set([
        data.trip.currency,
        ...data.trip.destinations.map((destination) => destination.currency),
        ...data.expenses.map((expense) => expense.currency),
      ].map((currency) => currency.toUpperCase())))
    : []

  const ratingMutation = useMutation({
    mutationFn: (rating: number) => rateTrip(numericTripId, rating),
    onSuccess: async (updatedTrip) => {
      queryClient.setQueryData(
        ['trip-details', numericTripId],
        (current: typeof data) =>
          current ? { ...current, trip: updatedTrip } : current,
      )
      await queryClient.invalidateQueries({ queryKey: ['trips'] })
      setRatingOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteTrip(numericTripId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['trips'] })
      navigate('/viajes', { replace: true })
    },
  })

  const openRating = () => {
    if (!data || data.trip.status !== 'completed') return
    setSelectedRating(data.trip.rating)
    ratingMutation.reset()
    setRatingOpen(true)
  }

  const openDelete = () => {
    deleteMutation.reset()
    setDeleteOpen(true)
  }

  const handleExport = async () => {
    if (!data) return
    setExporting(true)
    setExportError(false)
    try {
      const blob = await downloadTripExport(data.trip.id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${data.trip.name}.zip`
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      setExportError(true)
    } finally {
      setExporting(false)
    }
  }

  if (!Number.isInteger(numericTripId) || numericTripId < 1) {
    return <Alert severity="error">El identificador del viaje no es válido.</Alert>
  }

  return (
    <Box
      component="main"
      sx={{
        minHeight: '100dvh',
        px: { xs: 2, sm: 3, md: 5, lg: 6 },
        pt: { xs: 10, md: 5 },
        pb: 5,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 1400, mx: 'auto' }}>
        {isLoading && (
          <Box sx={{ minHeight: 500, display: 'grid', placeItems: 'center' }}>
            <CircularProgress />
          </Box>
        )}
        {isError && (
          <Alert
            severity="error"
            action={<Button color="inherit" onClick={() => refetch()}>Reintentar</Button>}
          >
            No se ha podido cargar el viaje. Comprueba la conexión e inténtalo de nuevo.
          </Alert>
        )}

        {data && (
          <>
            <Button
              component={RouterLink}
              to="/viajes"
              startIcon={<ArrowBackIcon />}
              sx={{ mb: 1, color: 'text.secondary' }}
            >
              Mis viajes
            </Button>

            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              sx={{
                gap: 2,
                alignItems: { sm: 'flex-start' },
                justifyContent: 'space-between',
              }}
            >
              <Box>
                <Stack
                  direction="row"
                  spacing={1.25}
                  sx={{ alignItems: 'center', flexWrap: 'wrap' }}
                >
                  <Typography
                    component="h1"
                    sx={{
                      fontSize: { xs: 30, md: 38 },
                      lineHeight: 1.1,
                      fontWeight: 850,
                      letterSpacing: -0.8,
                    }}
                  >
                    {data.trip.name}
                  </Typography>
                  <Chip
                    size="small"
                    variant="outlined"
                    color={statusConfig[data.trip.status].color}
                    label={statusConfig[data.trip.status].label}
                  />
                </Stack>
                <Stack
                  direction="row"
                  spacing={1}
                  sx={{
                    mt: 1,
                    color: 'text.secondary',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                  }}
                >
                  <Typography sx={{ fontSize: 13 }}>
                    Origen: {data.trip.origin}
                  </Typography>
                  <Typography>•</Typography>
                  <Typography sx={{ fontSize: 13 }}>
                    {data.trip.destinations
                      .slice()
                      .sort((a, b) => a.order - b.order)
                      .map((destination) => `${destination.city}, ${destination.country}`)
                      .join(' · ')}
                  </Typography>
                  <Typography>•</Typography>
                  <Typography sx={{ fontSize: 13 }}>
                    {formatDate(data.trip.start_date)} - {formatDate(data.trip.end_date)} ({data.trip.total_days} días)
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} sx={{ mt: 1.25, alignItems: 'center', flexWrap: 'wrap' }}>
                  <Typography sx={{ color: 'text.secondary', fontSize: 13, fontWeight: 700 }}>
                    Monedas utilizadas:
                  </Typography>
                  {usedCurrencies.map((currency) => (
                    <Chip key={currency} label={currency} size="small" variant="outlined" />
                  ))}
                  <CurrencyConverter currencies={usedCurrencies} />
                </Stack>
              </Box>
              <Stack
                direction="row"
                spacing={1}
                sx={{ flexWrap: 'wrap', justifyContent: { sm: 'flex-end' } }}
              >
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExport}
                  disabled={exporting || data.trip.status !== 'completed'}
                >
                  {exporting ? 'Exportando...' : 'Exportar'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<StarOutlineIcon />}
                  onClick={openRating}
                  disabled={data.trip.status !== 'completed'}
                >
                  {data.trip.rating
                    ? `Valoración: ${data.trip.rating}/5`
                    : 'Valorar'}
                </Button>
                <Button
                  component={RouterLink}
                  to={`/viajes/${data.trip.id}/editar`}
                  variant="contained"
                  startIcon={<EditOutlinedIcon />}
                >
                  Editar viaje
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteOutlineIcon />}
                  onClick={openDelete}
                >
                  Eliminar viaje
                </Button>
              </Stack>
            </Stack>

            {exportError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                No se ha podido exportar el viaje.
              </Alert>
            )}
            {data.trip.description && (
              <Typography
                sx={{
                  mt: 2,
                  maxWidth: 1000,
                  color: 'text.secondary',
                  lineHeight: 1.6,
                }}
              >
                {data.trip.description}
              </Typography>
            )}

            <Box
              sx={{
                mt: 3.5,
                display: 'grid',
                gridTemplateColumns: {
                  xs: '1fr',
                  lg: 'minmax(0, 1.65fr) minmax(320px, .9fr)',
                },
                gap: 2.5,
                alignItems: 'start',
              }}
            >
              <ActivitiesManager
                tripId={data.trip.id}
                totalDays={data.trip.total_days}
                initialActivities={data.activities}
              />

              <Stack spacing={2}>
                <ChecklistManager
                  tripId={data.trip.id}
                  initialTasks={data.tasks}
                />

                <ExpensesManager
                  tripId={data.trip.id}
                  tripStartDate={data.trip.start_date}
                  tripEndDate={data.trip.end_date}
                  tripCurrency={data.trip.currency}
                  budget={Number(data.trip.budget)}
                  participants={data.participants}
                  initialExpenses={data.expenses}
                />

                <ParticipantsManager
                  tripId={data.trip.id}
                  currency={data.trip.currency}
                  expenses={data.expenses}
                  initialParticipants={data.participants}
                />

                <TransportsManager
                  tripId={data.trip.id}
                  tripStartDate={data.trip.start_date}
                  tripEndDate={data.trip.end_date}
                  currency={data.trip.currency}
                  initialTransports={data.transports}
                />

                <AccommodationsManager
                  tripId={data.trip.id}
                  tripStartDate={data.trip.start_date}
                  tripEndDate={data.trip.end_date}
                  currency={data.trip.currency}
                  initialAccommodations={data.accommodations}
                />

                <NotesManager
                  tripId={data.trip.id}
                  totalDays={data.trip.total_days}
                  tripStatus={data.trip.status}
                  tripStartDate={data.trip.start_date}
                  initialNotes={data.notes}
                />

                <DocumentsManager
                  tripId={data.trip.id}
                  tripCompleted={data.trip.status === 'completed'}
                  initialFiles={data.files}
                />
              </Stack>
            </Box>
          </>
        )}

        <Dialog
          open={ratingOpen}
          onClose={() => !ratingMutation.isPending && setRatingOpen(false)}
          fullWidth
          maxWidth="xs"
        >
          <DialogTitle>Valorar viaje</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Selecciona una valoración para este viaje.
            </DialogContentText>
            <Box sx={{ mt: 3, display: 'grid', placeItems: 'center' }}>
              <Rating
                size="large"
                value={selectedRating}
                onChange={(_, value) => setSelectedRating(value)}
                disabled={ratingMutation.isPending}
              />
            </Box>
            {ratingMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                No se ha podido guardar la valoración.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => setRatingOpen(false)}
              disabled={ratingMutation.isPending}
            >
              Cancelar
            </Button>
            <Button
              variant="contained"
              disabled={!selectedRating || ratingMutation.isPending}
              onClick={() => {
                if (selectedRating) ratingMutation.mutate(selectedRating)
              }}
            >
              {ratingMutation.isPending
                ? 'Guardando...'
                : 'Guardar valoración'}
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog
          open={deleteOpen}
          onClose={() => !deleteMutation.isPending && setDeleteOpen(false)}
          fullWidth
          maxWidth="xs"
        >
          <DialogTitle>Eliminar viaje</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Esta acción eliminará el viaje y todos sus datos asociados de
              forma permanente. ¿Quieres continuar?
            </DialogContentText>
            {deleteMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                No se ha podido eliminar el viaje.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => setDeleteOpen(false)}
              disabled={deleteMutation.isPending}
            >
              Cancelar
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending
                ? 'Eliminando...'
                : 'Eliminar definitivamente'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  )
}
