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
  addTask,
  deleteTask,
  getTripTasks,
  reorderTasks,
  setTaskCompleted,
  updateTask,
} from '../../api/trips'
import type { TaskPayload, TripDetails, TripTask } from '../../types/trip'

const priorityConfig: Record<TripTask['priority'], { label: string; color: 'success' | 'warning' | 'error' }> = {
  low: { label: 'Baja', color: 'success' },
  medium: { label: 'Media', color: 'warning' },
  high: { label: 'Alta', color: 'error' },
}

function SortableTask({ task, busy, onToggle, onEdit, onDelete }: {
  task: TripTask
  busy: boolean
  onToggle: () => void
  onEdit: () => void
  onDelete: () => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: task.id })

  return (
    <Paper ref={setNodeRef} variant="outlined" sx={{ p: 0.75, display: 'flex', alignItems: 'center', borderRadius: '12px', borderColor: '#dce3ec', transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.7 : 1, zIndex: isDragging ? 2 : 1 }}>
      <IconButton size="small" aria-label={`Reordenar ${task.name}`} {...attributes} {...listeners} disabled={busy} sx={{ cursor: isDragging ? 'grabbing' : 'grab', touchAction: 'none' }}><DragIndicatorIcon fontSize="small" /></IconButton>
      <Checkbox size="small" checked={task.completed} onChange={onToggle} disabled={busy} slotProps={{ input: { 'aria-label': `Marcar ${task.name} como completada` } }} />
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography sx={{ fontSize: 13, fontWeight: 700, color: task.completed ? 'text.secondary' : 'text.primary', textDecoration: task.completed ? 'line-through' : 'none' }}>{task.name}</Typography>
        <Chip label={priorityConfig[task.priority].label} color={priorityConfig[task.priority].color} size="small" variant="outlined" sx={{ height: 20, fontSize: 10 }} />
      </Box>
      <IconButton size="small" aria-label={`Editar ${task.name}`} onClick={onEdit} disabled={busy}><EditOutlinedIcon fontSize="small" /></IconButton>
      <IconButton size="small" color="error" aria-label={`Eliminar ${task.name}`} onClick={onDelete} disabled={busy}><DeleteOutlineIcon fontSize="small" /></IconButton>
    </Paper>
  )
}

export function ChecklistManager({ tripId, initialTasks }: { tripId: number; initialTasks: TripTask[] }) {
  const queryClient = useQueryClient()
  const [tasks, setTasks] = useState(initialTasks.slice().sort((a, b) => a.order - b.order))
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TripTask | null>(null)
  const [toDelete, setToDelete] = useState<TripTask | null>(null)
  const [form, setForm] = useState<TaskPayload>({ name: '', priority: 'medium' })

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  const sync = (next: TripTask[]) => {
    const sorted = next.slice().sort((a, b) => a.order - b.order)
    setTasks(sorted)
    queryClient.setQueryData(['trip-details', tripId], (current: TripDetails | undefined) => current ? { ...current, tasks: sorted } : current)
  }

  const refresh = async () => sync(await getTripTasks(tripId))

  const saveMutation = useMutation({
    mutationFn: (payload: TaskPayload) => editing ? updateTask(tripId, editing.id, payload) : addTask(tripId, payload),
    onSuccess: async () => { await refresh(); setFormOpen(false) },
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteTask(tripId, id),
    onSuccess: async () => { await refresh(); setToDelete(null) },
  })
  const completionMutation = useMutation({
    mutationFn: ({ id, completed }: { id: number; completed: boolean }) => setTaskCompleted(tripId, id, completed),
    onSuccess: (updated) => sync(tasks.map((task) => task.id === updated.id ? updated : task)),
  })
  const reorderMutation = useMutation({
    mutationFn: (next: TripTask[]) => reorderTasks(tripId, { tasks: next.map((task, index) => ({ id: task.id, order: index + 1 })) }),
    onSuccess: sync,
    onError: () => refresh(),
  })

  const openCreate = () => {
    setEditing(null)
    setForm({ name: '', priority: 'medium' })
    saveMutation.reset()
    setFormOpen(true)
  }
  const openEdit = (task: TripTask) => {
    setEditing(task)
    setForm({ name: task.name, priority: task.priority })
    saveMutation.reset()
    setFormOpen(true)
  }
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id || reorderMutation.isPending) return
    const oldIndex = tasks.findIndex((task) => task.id === active.id)
    const newIndex = tasks.findIndex((task) => task.id === over.id)
    if (oldIndex < 0 || newIndex < 0) return
    const next = arrayMove(tasks, oldIndex, newIndex).map((task, index) => ({ ...task, order: index + 1 }))
    sync(next)
    reorderMutation.mutate(next)
  }

  const busy = saveMutation.isPending || deleteMutation.isPending || completionMutation.isPending || reorderMutation.isPending

  return (
    <Paper variant="outlined" sx={{ p: 2.25, borderRadius: '18px', borderColor: '#dce3ec' }}>
      <Stack direction="row" sx={{ mb: 1.5, gap: 1, alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography component="h2" sx={{ fontSize: 16, fontWeight: 800 }}>Checklist</Typography>
        <Button size="small" startIcon={<AddIcon />} onClick={openCreate} sx={{ minHeight: 32 }}>Añadir</Button>
      </Stack>
      {(deleteMutation.isError || completionMutation.isError || reorderMutation.isError) && <Alert severity="error" sx={{ mb: 2 }}>No se ha podido guardar el cambio. Inténtalo de nuevo.</Alert>}

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={tasks.map((task) => task.id)} strategy={verticalListSortingStrategy}>
          <Stack spacing={1}>
            {tasks.map((task) => <SortableTask key={task.id} task={task} busy={busy} onToggle={() => completionMutation.mutate({ id: task.id, completed: !task.completed })} onEdit={() => openEdit(task)} onDelete={() => { deleteMutation.reset(); setToDelete(task) }} />)}
            {!tasks.length && <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>No hay tareas en la checklist.</Typography>}
          </Stack>
        </SortableContext>
      </DndContext>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={(event) => { event.preventDefault(); saveMutation.mutate({ ...form, name: form.name.trim() }) }}>
          <DialogTitle>{editing ? 'Editar tarea' : 'Añadir tarea'}</DialogTitle>
          <DialogContent>
            {saveMutation.isError && <Alert severity="error" sx={{ mb: 2 }}>No se ha podido guardar la tarea. Revisa sus datos.</Alert>}
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField label="Nombre" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required slotProps={{ htmlInput: { maxLength: 150 } }} />
              <TextField select label="Prioridad" value={form.priority} onChange={(event) => setForm((current) => ({ ...current, priority: event.target.value as TripTask['priority'] }))}>
                {Object.entries(priorityConfig).map(([value, config]) => <MenuItem key={value} value={value}>{config.label}</MenuItem>)}
              </TextField>
            </Stack>
          </DialogContent>
          <DialogActions><Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>Cancelar</Button><Button type="submit" variant="contained" disabled={saveMutation.isPending}>{saveMutation.isPending ? 'Guardando...' : 'Guardar tarea'}</Button></DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(toDelete)} onClose={() => !deleteMutation.isPending && setToDelete(null)} fullWidth maxWidth="xs">
        <DialogTitle>Eliminar tarea</DialogTitle>
        <DialogContent><DialogContentText>¿Quieres eliminar «{toDelete?.name}» de la checklist?</DialogContentText></DialogContent>
        <DialogActions><Button onClick={() => setToDelete(null)} disabled={deleteMutation.isPending}>Cancelar</Button><Button color="error" variant="contained" disabled={deleteMutation.isPending} onClick={() => { if (toDelete) deleteMutation.mutate(toDelete.id) }}>{deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}</Button></DialogActions>
      </Dialog>
    </Paper>
  )
}
