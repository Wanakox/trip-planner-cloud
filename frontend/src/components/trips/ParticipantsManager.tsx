import AddIcon from '@mui/icons-material/Add'
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
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useMemo, useState } from 'react'

import {
  addParticipant,
  deleteParticipant,
  getExpenseSummary,
  getTripParticipants,
  updateParticipant,
} from '../../api/trips'
import { getCurrentUser } from '../../api/user'
import { UserAvatar } from '../UserAvatar'
import type {
  TripDetails,
  TripExpense,
  TripParticipant,
} from '../../types/trip'

function initials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

function deleteErrorMessage(error: unknown) {
  if (axios.isAxiosError(error) && error.response?.status === 409) {
    return 'No se puede eliminar porque tiene gastos asociados. Elimina o reasigna primero sus gastos.'
  }
  if (axios.isAxiosError(error) && error.response?.status === 401) {
    return 'Tu sesión ha caducado. Inicia sesión de nuevo.'
  }
  return 'No se ha podido eliminar el participante.'
}

export function ParticipantsManager({
  tripId,
  currency,
  expenses,
  initialParticipants,
}: {
  tripId: number
  currency: string
  expenses: TripExpense[]
  initialParticipants: TripParticipant[]
}) {
  const queryClient = useQueryClient()
  const [participants, setParticipants] = useState(initialParticipants)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TripParticipant | null>(null)
  const [toDelete, setToDelete] = useState<TripParticipant | null>(null)
  const [name, setName] = useState('')

  const summaryQuery = useQuery({
    queryKey: ['expense-summary', tripId],
    queryFn: () => getExpenseSummary(tripId),
  })
  const profileQuery = useQuery({
    queryKey: ['current-user'],
    queryFn: getCurrentUser,
  })
  const ownerParticipantId = participants.length
    ? Math.min(...participants.map((participant) => participant.id))
    : null
  const ownerName = profileQuery.data
    ? `${profileQuery.data.name} ${profileQuery.data.surname}`.trim().toLocaleLowerCase()
    : ''

  const totals = useMemo(
    () => summaryQuery.data
      ? summaryQuery.data.participants.reduce<Record<number, number>>((result, participant) => {
          result[participant.participant_id] = Number(participant.total_expenses)
          return result
        }, {})
      : expenses.reduce<Record<number, number>>((result, expense) => {
      result[expense.participant_id] = (result[expense.participant_id] ?? 0) + Number(expense.amount)
      return result
    }, {}),
    [expenses, summaryQuery.data],
  )

  const formatMoney = (amount: number) => new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency,
  }).format(amount)

  const sync = (next: TripParticipant[]) => {
    setParticipants(next)
    queryClient.setQueryData(
      ['trip-details', tripId],
      (current: TripDetails | undefined) => current ? { ...current, participants: next } : current,
    )
  }

  const refresh = async () => sync(await getTripParticipants(tripId))

  const saveMutation = useMutation({
    mutationFn: (participantName: string) => editing
      ? updateParticipant(tripId, editing.id, { name: participantName })
      : addParticipant(tripId, { name: participantName }),
    onSuccess: async () => {
      await refresh()
      setFormOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (participantId: number) => deleteParticipant(tripId, participantId),
    onSuccess: async () => {
      await refresh()
      setToDelete(null)
    },
  })

  const openCreate = () => {
    setEditing(null)
    setName('')
    saveMutation.reset()
    setFormOpen(true)
  }

  const openEdit = (participant: TripParticipant) => {
    setEditing(participant)
    setName(participant.name)
    saveMutation.reset()
    setFormOpen(true)
  }

  return (
    <Paper variant="outlined" sx={{ p: 2.25, borderRadius: '18px', borderColor: '#dce3ec' }}>
      <Stack direction="row" sx={{ mb: 1.5, gap: 1, alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography component="h2" sx={{ fontSize: 16, fontWeight: 800 }}>Participantes</Typography>
        <Button size="small" startIcon={<AddIcon />} onClick={openCreate} sx={{ minHeight: 32 }}>Añadir</Button>
      </Stack>

      {deleteMutation.isError && <Alert severity="error" sx={{ mb: 2 }}>{deleteErrorMessage(deleteMutation.error)}</Alert>}

      <Stack spacing={1}>
        {participants.map((participant) => (
          <Stack key={participant.id} direction="row" spacing={1.25} sx={{ p: 1, alignItems: 'center', bgcolor: '#f7f9fc', borderRadius: '12px' }}>
            {profileQuery.data && (
              participant.id === ownerParticipantId
              || participant.name.trim().toLocaleLowerCase() === ownerName
            )
              ? <UserAvatar user={profileQuery.data} size={34} />
              : <Avatar sx={{ width: 34, height: 34, bgcolor: 'primary.light', color: 'primary.main', fontSize: 12, fontWeight: 800 }}>{initials(participant.name)}</Avatar>}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography noWrap sx={{ fontSize: 13, fontWeight: 750 }}>{participant.name}</Typography>
              <Typography sx={{ color: 'text.secondary', fontSize: 12 }}>
                Gastos totales: {formatMoney(totals[participant.id] ?? 0)}
              </Typography>
            </Box>
            <IconButton size="small" aria-label={`Editar ${participant.name}`} onClick={() => openEdit(participant)}><EditOutlinedIcon fontSize="small" /></IconButton>
            <IconButton size="small" color="error" aria-label={`Eliminar ${participant.name}`} onClick={() => { deleteMutation.reset(); setToDelete(participant) }}><DeleteOutlineIcon fontSize="small" /></IconButton>
          </Stack>
        ))}
        {!participants.length && <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>No hay participantes registrados.</Typography>}
      </Stack>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={(event) => { event.preventDefault(); saveMutation.mutate(name.trim()) }}>
          <DialogTitle>{editing ? 'Editar participante' : 'Añadir participante'}</DialogTitle>
          <DialogContent>
            {saveMutation.isError && <Alert severity="error" sx={{ mb: 2 }}>No se ha podido guardar el participante. Revisa el nombre.</Alert>}
            <TextField autoFocus fullWidth label="Nombre" value={name} onChange={(event) => setName(event.target.value)} required sx={{ mt: 1 }} slotProps={{ htmlInput: { maxLength: 150 } }} />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={saveMutation.isPending}>{saveMutation.isPending ? 'Guardando...' : 'Guardar participante'}</Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(toDelete)} onClose={() => !deleteMutation.isPending && setToDelete(null)} fullWidth maxWidth="xs">
        <DialogTitle>Eliminar participante</DialogTitle>
        <DialogContent>
          <DialogContentText>¿Quieres eliminar a «{toDelete?.name}» del viaje?</DialogContentText>
          {toDelete && (totals[toDelete.id] ?? 0) > 0 && <Alert severity="warning" sx={{ mt: 2 }}>Este participante tiene gastos asociados y no podrá eliminarse hasta que se eliminen o reasignen.</Alert>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setToDelete(null)} disabled={deleteMutation.isPending}>Cancelar</Button>
          <Button color="error" variant="contained" disabled={deleteMutation.isPending || Boolean(toDelete && (totals[toDelete.id] ?? 0) > 0)} onClick={() => { if (toDelete) deleteMutation.mutate(toDelete.id) }}>{deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  )
}
