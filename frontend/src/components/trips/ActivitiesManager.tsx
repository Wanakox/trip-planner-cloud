import AccessTimeIcon from '@mui/icons-material/AccessTime'
import AddIcon from '@mui/icons-material/Add'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined'
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
  Checkbox,
  Chip,
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
  addActivity,
  deleteActivity,
  getTripActivities,
  reorderActivities,
  setActivityCompleted,
  updateActivity,
} from '../../api/trips'
import type {
  ActivityPayload,
  TripActivity,
  TripDetails,
} from '../../types/trip'

const emptyForm: ActivityPayload = {
  name: '',
  location: null,
  start_time: null,
  day_number: 1,
}

function normalizeOrders(activities: TripActivity[]) {
  const nextOrderByDay = new Map<number, number>()

  return activities
    .slice()
    .sort(
      (first, second) =>
        first.day_number - second.day_number ||
        first.order - second.order,
    )
    .map((activity) => {
      const nextOrder =
        (nextOrderByDay.get(activity.day_number) ?? 0) + 1
      nextOrderByDay.set(activity.day_number, nextOrder)

      return { ...activity, order: nextOrder }
    })
}

function SortableActivity({
  activity,
  busy,
  onToggle,
  onEdit,
  onDelete,
}: {
  activity: TripActivity
  busy: boolean
  onToggle: () => void
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
  } = useSortable({ id: activity.id })

  return (
    <Paper
      ref={setNodeRef}
      variant="outlined"
      sx={{
        p: 2,
        display: 'flex',
        gap: 1,
        alignItems: 'flex-start',
        borderRadius: '16px',
        borderColor: '#dce3ec',
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.7 : 1,
        zIndex: isDragging ? 2 : 1,
      }}
    >
      <IconButton
        aria-label={`Reordenar ${activity.name}`}
        {...attributes}
        {...listeners}
        disabled={busy}
        sx={{ cursor: isDragging ? 'grabbing' : 'grab', touchAction: 'none' }}
      >
        <DragIndicatorIcon />
      </IconButton>
      <Checkbox
        checked={activity.completed}
        onChange={onToggle}
        disabled={busy}
        slotProps={{
          input: {
            'aria-label': `Marcar ${activity.name} como completada`,
          },
        }}
      />
      <Box sx={{ flex: 1, minWidth: 0, pt: 0.75 }}>
        <Typography
          sx={{
            fontWeight: 750,
            textDecoration: activity.completed ? 'line-through' : 'none',
            color: activity.completed ? 'text.secondary' : 'text.primary',
          }}
        >
          {activity.name}
        </Typography>
        <Stack
          direction="row"
          spacing={1.5}
          sx={{ mt: 0.6, flexWrap: 'wrap', color: 'text.secondary' }}
        >
          {activity.start_time && (
            <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
              <AccessTimeIcon sx={{ fontSize: 16 }} />
              <Typography sx={{ fontSize: 12 }}>
                {activity.start_time.slice(0, 5)}
              </Typography>
            </Stack>
          )}
          {activity.location && (
            <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
              <LocationOnOutlinedIcon sx={{ fontSize: 16 }} />
              <Typography sx={{ fontSize: 12 }}>{activity.location}</Typography>
            </Stack>
          )}
        </Stack>
      </Box>
      <IconButton aria-label={`Editar ${activity.name}`} onClick={onEdit} disabled={busy}>
        <EditOutlinedIcon />
      </IconButton>
      <IconButton
        aria-label={`Eliminar ${activity.name}`}
        onClick={onDelete}
        disabled={busy}
        color="error"
      >
        <DeleteOutlineIcon />
      </IconButton>
    </Paper>
  )
}

export function ActivitiesManager({
  tripId,
  totalDays,
  initialActivities,
}: {
  tripId: number
  totalDays: number
  initialActivities: TripActivity[]
}) {
  const queryClient = useQueryClient()
  const [activities, setActivities] = useState(initialActivities)
  const [formOpen, setFormOpen] = useState(false)
  const [editingActivity, setEditingActivity] = useState<TripActivity | null>(null)
  const [activityToDelete, setActivityToDelete] = useState<TripActivity | null>(null)
  const [form, setForm] = useState<ActivityPayload>(emptyForm)

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  const syncActivities = (nextActivities: TripActivity[]) => {
    setActivities(nextActivities)
    queryClient.setQueryData(
      ['trip-details', tripId],
      (current: TripDetails | undefined) =>
        current ? { ...current, activities: nextActivities } : current,
    )
  }

  const refreshActivities = async () => {
    const nextActivities = await getTripActivities(tripId)
    syncActivities(nextActivities)
  }

  const saveMutation = useMutation({
    mutationFn: () =>
      editingActivity
        ? updateActivity(tripId, editingActivity.id, form)
        : addActivity(tripId, form),
    onSuccess: async () => {
      await refreshActivities()
      setFormOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (activityId: number) => deleteActivity(tripId, activityId),
    onSuccess: async () => {
      await refreshActivities()
      setActivityToDelete(null)
    },
  })

  const completionMutation = useMutation({
    mutationFn: ({ activityId, completed }: { activityId: number; completed: boolean }) =>
      setActivityCompleted(tripId, activityId, completed),
    onSuccess: (updatedActivity) => {
      syncActivities(
        activities.map((activity) =>
          activity.id === updatedActivity.id ? updatedActivity : activity,
        ),
      )
    },
  })

  const reorderMutation = useMutation({
    mutationFn: (nextActivities: TripActivity[]) =>
      reorderActivities(tripId, {
        activities: normalizeOrders(nextActivities).map((activity) => ({
          id: activity.id,
          day_number: activity.day_number,
          order: activity.order,
        })),
      }),
    onSuccess: syncActivities,
    onError: () => refreshActivities(),
  })

  const activitiesByDay = Array.from({ length: totalDays }, (_, index) => {
    const dayNumber = index + 1
    return {
      dayNumber,
      activities: activities
        .filter((activity) => activity.day_number === dayNumber)
        .sort((a, b) => a.order - b.order),
    }
  }).filter((day) => day.activities.length > 0)

  const openCreate = () => {
    setEditingActivity(null)
    setForm({ ...emptyForm, day_number: 1 })
    saveMutation.reset()
    setFormOpen(true)
  }

  const openEdit = (activity: TripActivity) => {
    setEditingActivity(activity)
    setForm({
      name: activity.name,
      location: activity.location,
      start_time: activity.start_time?.slice(0, 5) ?? null,
      day_number: activity.day_number,
    })
    saveMutation.reset()
    setFormOpen(true)
  }

  const handleDragEnd = (dayNumber: number, event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id || reorderMutation.isPending) return
    const dayActivities = activities
      .filter((activity) => activity.day_number === dayNumber)
      .sort((a, b) => a.order - b.order)
    const oldIndex = dayActivities.findIndex((activity) => activity.id === active.id)
    const newIndex = dayActivities.findIndex((activity) => activity.id === over.id)
    if (oldIndex < 0 || newIndex < 0) return
    const reorderedDay = arrayMove(dayActivities, oldIndex, newIndex).map(
      (activity, index) => ({ ...activity, order: index + 1 }),
    )
    const reorderedIds = new Set(reorderedDay.map((activity) => activity.id))
    const nextActivities = normalizeOrders(activities
      .filter((activity) => !reorderedIds.has(activity.id))
      .concat(reorderedDay))
    syncActivities(nextActivities)
    reorderMutation.mutate(nextActivities)
  }

  const busy =
    saveMutation.isPending ||
    deleteMutation.isPending ||
    completionMutation.isPending ||
    reorderMutation.isPending

  return (
    <Box>
      <Stack
        direction="row"
        sx={{ mb: 1.5, alignItems: 'center', justifyContent: 'space-between' }}
      >
        <Typography component="h2" sx={{ fontSize: 19, fontWeight: 850 }}>
          Itinerario diario
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
          Añadir actividad
        </Button>
      </Stack>

      {(deleteMutation.isError || completionMutation.isError || reorderMutation.isError) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          No se ha podido guardar el cambio. Inténtalo de nuevo.
        </Alert>
      )}

      <Stack spacing={2.5}>
        {activitiesByDay.map((day) => (
          <Box key={day.dayNumber}>
            <Chip
              label={`DÍA ${day.dayNumber}`}
              size="small"
              color="primary"
              sx={{ mb: 1, fontWeight: 800 }}
            />
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={(event) => handleDragEnd(day.dayNumber, event)}
            >
              <SortableContext
                items={day.activities.map((activity) => activity.id)}
                strategy={verticalListSortingStrategy}
              >
                <Stack spacing={1.25}>
                  {day.activities.map((activity) => (
                    <SortableActivity
                      key={activity.id}
                      activity={activity}
                      busy={busy}
                      onToggle={() =>
                        completionMutation.mutate({
                          activityId: activity.id,
                          completed: !activity.completed,
                        })
                      }
                      onEdit={() => openEdit(activity)}
                      onDelete={() => {
                        deleteMutation.reset()
                        setActivityToDelete(activity)
                      }}
                    />
                  ))}
                </Stack>
              </SortableContext>
            </DndContext>
          </Box>
        ))}
        {!activities.length && (
          <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
            <Typography sx={{ color: 'text.secondary' }}>
              Aún no hay actividades en este viaje.
            </Typography>
          </Paper>
        )}
      </Stack>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={(event) => { event.preventDefault(); saveMutation.mutate() }}>
          <DialogTitle>{editingActivity ? 'Editar actividad' : 'Añadir actividad'}</DialogTitle>
          <DialogContent>
            {saveMutation.isError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                No se ha podido guardar la actividad. Revisa sus datos.
              </Alert>
            )}
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Nombre"
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                required
              />
              <TextField
                label="Ubicación"
                value={form.location ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, location: event.target.value || null }))}
              />
              <TextField
                label="Hora de inicio"
                type="time"
                value={form.start_time ?? ''}
                onChange={(event) => setForm((current) => ({ ...current, start_time: event.target.value || null }))}
                slotProps={{ inputLabel: { shrink: true } }}
              />
              <TextField
                select
                label="Día del viaje"
                value={form.day_number}
                onChange={(event) => setForm((current) => ({ ...current, day_number: Number(event.target.value) }))}
              >
                {Array.from({ length: totalDays }, (_, index) => index + 1).map((day) => (
                  <MenuItem key={day} value={day}>Día {day}</MenuItem>
                ))}
              </TextField>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Guardando...' : 'Guardar actividad'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog
        open={Boolean(activityToDelete)}
        onClose={() => !deleteMutation.isPending && setActivityToDelete(null)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Eliminar actividad</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Quieres eliminar «{activityToDelete?.name}» del itinerario?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActivityToDelete(null)} disabled={deleteMutation.isPending}>Cancelar</Button>
          <Button
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (activityToDelete) deleteMutation.mutate(activityToDelete.id)
            }}
          >
            {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
