import AddIcon from '@mui/icons-material/Add'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  Alert,
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
import { useState } from 'react'

import {
  addDestination,
  deleteDestination,
  reorderDestinations,
  updateDestination,
} from '../../api/trips'
import type { Currency } from '../../api/currency'
import type {
  Destination,
  DestinationCreatePayload,
  Trip,
  TripDetails,
} from '../../types/trip'

type DestinationForm = DestinationCreatePayload

const emptyDestination: DestinationForm = {
  country: '',
  city: '',
  currency: 'EUR',
}

function SortableDestination({
  destination,
  disableDelete,
  onEdit,
  onDelete,
}: {
  destination: Destination
  disableDelete: boolean
  onEdit: () => void
  onDelete: () => void
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: destination.id })

  return (
    <Paper
      ref={setNodeRef}
      variant="outlined"
      sx={{
        p: 2,
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        borderRadius: '14px',
        borderColor: '#dce3ec',
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.7 : 1,
        zIndex: isDragging ? 2 : 1,
      }}
    >
      <IconButton
        aria-label={`Reorganizar ${destination.city}`}
        {...attributes}
        {...listeners}
        sx={{ cursor: isDragging ? 'grabbing' : 'grab', touchAction: 'none' }}
      >
        <DragIndicatorIcon />
      </IconButton>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography sx={{ fontWeight: 800 }}>
          {destination.city}
        </Typography>
        <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>
          {destination.country} · {destination.currency}
        </Typography>
      </Box>
      <IconButton aria-label={`Editar ${destination.city}`} onClick={onEdit}>
        <EditOutlinedIcon />
      </IconButton>
      <IconButton
        aria-label={`Eliminar ${destination.city}`}
        color="error"
        onClick={onDelete}
        disabled={disableDelete}
      >
        <DeleteOutlineIcon />
      </IconButton>
    </Paper>
  )
}

export function DestinationsManager({
  tripId,
  initialDestinations,
  currencies,
}: {
  tripId: number
  initialDestinations: Destination[]
  currencies: Currency[]
}) {
  const queryClient = useQueryClient()
  const [destinations, setDestinations] = useState(() =>
    initialDestinations.slice().sort((a, b) => a.order - b.order),
  )
  const [formOpen, setFormOpen] = useState(false)
  const [editingDestination, setEditingDestination] =
    useState<Destination | null>(null)
  const [destinationToDelete, setDestinationToDelete] =
    useState<Destination | null>(null)
  const [form, setForm] = useState<DestinationForm>(emptyDestination)

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  )

  const syncTrip = async (trip: Trip) => {
    const ordered = trip.destinations.slice().sort((a, b) => a.order - b.order)
    setDestinations(ordered)
    queryClient.setQueryData(['trip', tripId], trip)
    queryClient.setQueryData(
      ['trip-details', tripId],
      (current: TripDetails | undefined) =>
        current ? { ...current, trip } : current,
    )
    await queryClient.invalidateQueries({ queryKey: ['trips'] })
  }

  const saveMutation = useMutation({
    mutationFn: () =>
      editingDestination
        ? updateDestination(tripId, editingDestination.id, form)
        : addDestination(tripId, form),
    onSuccess: async (trip) => {
      await syncTrip(trip)
      setFormOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (destinationId: number) =>
      deleteDestination(tripId, destinationId),
    onSuccess: async (trip) => {
      await syncTrip(trip)
      setDestinationToDelete(null)
    },
  })

  const reorderMutation = useMutation({
    mutationFn: (orderedDestinations: Destination[]) =>
      reorderDestinations(tripId, {
        destinations: orderedDestinations.map((destination, index) => ({
          id: destination.id,
          order: index + 1,
        })),
      }),
    onSuccess: syncTrip,
    onError: () => setDestinations(destinations),
  })

  const openCreate = () => {
    setEditingDestination(null)
    setForm({ ...emptyDestination, currency: currencies[0]?.code ?? 'EUR' })
    saveMutation.reset()
    setFormOpen(true)
  }

  const openEdit = (destination: Destination) => {
    setEditingDestination(destination)
    setForm({
      country: destination.country,
      city: destination.city,
      currency: destination.currency,
    })
    saveMutation.reset()
    setFormOpen(true)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id || reorderMutation.isPending) return
    const oldIndex = destinations.findIndex((item) => item.id === active.id)
    const newIndex = destinations.findIndex((item) => item.id === over.id)
    if (oldIndex < 0 || newIndex < 0) return
    const reordered = arrayMove(destinations, oldIndex, newIndex)
    setDestinations(reordered)
    reorderMutation.mutate(reordered)
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    saveMutation.mutate()
  }

  return (
    <Paper
      variant="outlined"
      sx={{ mt: 3, p: { xs: 2.5, sm: 4 }, borderRadius: '22px', borderColor: '#dce3ec' }}
    >
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={2}
        sx={{ alignItems: { sm: 'center' }, justifyContent: 'space-between' }}
      >
        <Box>
          <Typography component="h2" sx={{ fontSize: 21, fontWeight: 800 }}>
            Destinos
          </Typography>
          <Typography sx={{ mt: 0.5, color: 'text.secondary', fontSize: 14 }}>
            Arrastra los destinos para cambiar el orden del recorrido.
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={openCreate}
          disabled={destinations.length >= 20}
        >
          Añadir destino
        </Button>
      </Stack>

      {(reorderMutation.isError || deleteMutation.isError) && (
        <Alert severity="error" sx={{ mt: 2 }}>
          No se ha podido guardar el cambio. Inténtalo de nuevo.
        </Alert>
      )}

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={destinations.map((destination) => destination.id)}
          strategy={verticalListSortingStrategy}
        >
          <Stack spacing={1.5} sx={{ mt: 3 }}>
            {destinations.map((destination) => (
              <SortableDestination
                key={destination.id}
                destination={destination}
                disableDelete={destinations.length === 1}
                onEdit={() => openEdit(destination)}
                onDelete={() => {
                  deleteMutation.reset()
                  setDestinationToDelete(destination)
                }}
              />
            ))}
          </Stack>
        </SortableContext>
      </DndContext>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={handleSubmit}>
          <DialogTitle>
            {editingDestination ? 'Editar destino' : 'Añadir destino'}
          </DialogTitle>
          <DialogContent>
            {saveMutation.isError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                No se ha podido guardar el destino. Revisa los datos introducidos.
              </Alert>
            )}
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="País"
                value={form.country}
                onChange={(event) => setForm((current) => ({ ...current, country: event.target.value }))}
                required
              />
              <TextField
                label="Ciudad"
                value={form.city}
                onChange={(event) => setForm((current) => ({ ...current, city: event.target.value }))}
                required
              />
              <TextField
                select
                label="Moneda"
                value={form.currency}
                onChange={(event) => setForm((current) => ({ ...current, currency: event.target.value }))}
                required
              >
                {currencies.map((currency) => (
                  <MenuItem key={currency.code} value={currency.code}>
                    {currency.code} — {currency.name}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Guardando...' : 'Guardar destino'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog
        open={Boolean(destinationToDelete)}
        onClose={() => !deleteMutation.isPending && setDestinationToDelete(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Eliminar destino</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Quieres eliminar {destinationToDelete?.city} del viaje?
          </DialogContentText>
          {deleteMutation.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              No se ha podido eliminar el destino.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDestinationToDelete(null)} disabled={deleteMutation.isPending}>
            Cancelar
          </Button>
          <Button
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (destinationToDelete) deleteMutation.mutate(destinationToDelete.id)
            }}
          >
            {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}
