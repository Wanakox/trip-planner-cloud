import AddIcon from '@mui/icons-material/Add'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  IconButton,
  LinearProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useMemo, useState } from 'react'

import {
  addExpense,
  deleteExpense,
  getExpenseSummary,
  getTripExpenses,
  updateExpense,
} from '../../api/trips'
import { getCurrencies } from '../../api/currency'
import type {
  ExpensePayload,
  TripDetails,
  TripExpense,
  TripParticipant,
} from '../../types/trip'

const categories: Record<TripExpense['category'], string> = {
  accommodation: 'Alojamiento',
  transport: 'Transporte',
  food: 'Comidas',
  leisure: 'Ocio',
  shopping: 'Compras',
  other: 'Varios',
}

function emptyForm(
  participantId: number,
  currency: string,
  date: string,
): ExpensePayload {
  return {
    participant_id: participantId,
    name: '',
    amount: 0,
    category: 'other',
    currency,
    expense_date: date,
  }
}

function saveErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error)) return 'No se ha podido guardar el gasto.'
  if (!error.response) return 'No se puede conectar con el servidor.'
  if (error.response.status === 401) return 'Tu sesión ha caducado. Inicia sesión de nuevo.'
  if (error.response.status === 404) return 'El participante seleccionado ya no existe.'
  if (Array.isArray(error.response.data?.detail)) {
    return `Revisa los datos: ${error.response.data.detail[0]?.msg ?? 'hay un valor no válido'}.`
  }
  return 'No se ha podido guardar el gasto. Revisa los datos introducidos.'
}

export function ExpensesManager({
  tripId,
  tripStartDate,
  tripEndDate,
  tripCurrency,
  budget,
  participants,
  initialExpenses,
}: {
  tripId: number
  tripStartDate: string
  tripEndDate: string
  tripCurrency: string
  budget: number
  participants: TripParticipant[]
  initialExpenses: TripExpense[]
}) {
  const queryClient = useQueryClient()
  const [expenses, setExpenses] = useState(initialExpenses)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<TripExpense | null>(null)
  const [toDelete, setToDelete] = useState<TripExpense | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [form, setForm] = useState<ExpensePayload>(() =>
    emptyForm(participants[0]?.id ?? 0, tripCurrency, tripStartDate),
  )

  const summaryQuery = useQuery({
    queryKey: ['expense-summary', tripId],
    queryFn: () => getExpenseSummary(tripId),
  })
  const currenciesQuery = useQuery({
    queryKey: ['currencies'],
    queryFn: getCurrencies,
  })

  const participantNames = useMemo(
    () => new Map(participants.map((participant) => [participant.id, participant.name])),
    [participants],
  )

  const fallbackTotal = expenses.reduce((total, expense) =>
    expense.currency === tripCurrency ? total + Number(expense.amount) : total, 0)
  const total = summaryQuery.data ? Number(summaryQuery.data.total_expenses) : fallbackTotal
  const remaining = summaryQuery.data?.remaining_budget === null
    ? null
    : Number(summaryQuery.data?.remaining_budget ?? budget - fallbackTotal)

  const formatMoney = (amount: number, currency = tripCurrency) =>
    new Intl.NumberFormat('es-ES', { style: 'currency', currency }).format(amount)

  const sync = (next: TripExpense[]) => {
    setExpenses(next)
    queryClient.setQueryData(
      ['trip-details', tripId],
      (current: TripDetails | undefined) => current ? { ...current, expenses: next } : current,
    )
  }

  const refresh = async () => {
    sync(await getTripExpenses(tripId))
    await queryClient.invalidateQueries({ queryKey: ['expense-summary', tripId] })
  }

  const saveMutation = useMutation({
    mutationFn: (payload: ExpensePayload) => editing
      ? updateExpense(tripId, editing.id, payload)
      : addExpense(tripId, payload),
    onSuccess: async () => {
      await refresh()
      setFormOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (expenseId: number) => deleteExpense(tripId, expenseId),
    onSuccess: async () => {
      await refresh()
      setToDelete(null)
    },
  })

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm(participants[0]?.id ?? 0, tripCurrency, tripStartDate))
    setValidationError(null)
    saveMutation.reset()
    setFormOpen(true)
  }

  const openEdit = (expense: TripExpense) => {
    setEditing(expense)
    setForm({
      participant_id: expense.participant_id,
      name: expense.name,
      amount: Number(expense.amount),
      category: expense.category,
      currency: expense.currency,
      expense_date: expense.expense_date,
    })
    setValidationError(null)
    saveMutation.reset()
    setFormOpen(true)
  }

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const name = form.name.trim()
    const currency = form.currency.trim().toUpperCase()
    setValidationError(null)

    if (!participants.some((participant) => participant.id === form.participant_id)) {
      setValidationError('Selecciona un participante válido.')
      return
    }
    if (!name || form.amount <= 0) {
      setValidationError('Indica un nombre y una cantidad superior a cero.')
      return
    }
    if (!/^[A-Z]{3}$/.test(currency)) {
      setValidationError('La moneda debe ser un código de tres letras, por ejemplo EUR.')
      return
    }
    if (form.expense_date < tripStartDate || form.expense_date > tripEndDate) {
      setValidationError('La fecha debe estar dentro de las fechas del viaje.')
      return
    }

    const payload = { ...form, name, currency }
    setForm(payload)
    saveMutation.mutate(payload)
  }

  return (
    <Paper variant="outlined" sx={{ p: 2.25, borderRadius: '18px', borderColor: '#dce3ec' }}>
      <Stack direction="row" sx={{ mb: 1.5, gap: 1, alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography component="h2" sx={{ fontSize: 16, fontWeight: 800 }}>Gastos</Typography>
        <Button size="small" startIcon={<AddIcon />} onClick={openCreate} disabled={!participants.length} sx={{ minHeight: 32 }}>Añadir</Button>
      </Stack>

      {!participants.length && <Alert severity="info" sx={{ mb: 2 }}>Añade primero un participante para poder registrar gastos.</Alert>}
      {(deleteMutation.isError || summaryQuery.isError) && <Alert severity="error" sx={{ mb: 2 }}>{summaryQuery.isError ? 'No se ha podido calcular el resumen. Comprueba las monedas o inténtalo de nuevo.' : 'No se ha podido eliminar el gasto.'}</Alert>}

      <Stack spacing={1}>
        {expenses.map((expense) => (
          <Stack key={expense.id} direction="row" spacing={1} sx={{ p: 1, alignItems: 'center', bgcolor: '#f7f9fc', borderRadius: '12px' }}>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography noWrap sx={{ fontSize: 13, fontWeight: 750 }}>{expense.name}</Typography>
              <Typography sx={{ color: 'text.secondary', fontSize: 11 }}>{participantNames.get(expense.participant_id) ?? 'Participante'} · {categories[expense.category]} · {new Intl.DateTimeFormat('es-ES').format(new Date(`${expense.expense_date}T00:00:00`))}</Typography>
            </Box>
            <Typography sx={{ fontSize: 13, fontWeight: 800 }}>{formatMoney(Number(expense.amount), expense.currency)}</Typography>
            <IconButton size="small" aria-label={`Editar ${expense.name}`} onClick={() => openEdit(expense)}><EditOutlinedIcon fontSize="small" /></IconButton>
            <IconButton size="small" color="error" aria-label={`Eliminar ${expense.name}`} onClick={() => { deleteMutation.reset(); setToDelete(expense) }}><DeleteOutlineIcon fontSize="small" /></IconButton>
          </Stack>
        ))}
        {!expenses.length && <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>Todavía no hay gastos registrados.</Typography>}
      </Stack>

      <Divider sx={{ my: 2 }} />
      <Stack spacing={1}>
        <Stack direction="row" sx={{ justifyContent: 'space-between' }}><Typography sx={{ color: 'text.secondary', fontSize: 13 }}>Total gastado</Typography><Typography sx={{ fontWeight: 800 }}>{formatMoney(total)}</Typography></Stack>
        <LinearProgress variant="determinate" color={total > budget ? 'error' : 'primary'} value={budget > 0 ? Math.min((total / budget) * 100, 100) : 0} sx={{ height: 6, borderRadius: 4 }} />
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
          <Chip size="small" variant="outlined" label={`Presupuesto: ${formatMoney(budget)}`} />
          {remaining !== null && <Typography sx={{ fontSize: 12, fontWeight: 700, color: remaining < 0 ? 'error.main' : 'success.main' }}>{remaining < 0 ? `Excedido: ${formatMoney(Math.abs(remaining))}` : `Disponible: ${formatMoney(remaining)}`}</Typography>}
        </Stack>
      </Stack>

      <Dialog open={formOpen} onClose={() => !saveMutation.isPending && setFormOpen(false)} fullWidth maxWidth="md">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>{editing ? 'Editar gasto' : 'Añadir gasto'}</DialogTitle>
          <DialogContent>
            {(validationError || saveMutation.isError) && <Alert severity="error" sx={{ mb: 2 }}>{validationError || saveErrorMessage(saveMutation.error)}</Alert>}
            <Box sx={{ mt: 1, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
              <TextField label="Concepto" value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required slotProps={{ htmlInput: { maxLength: 150 } }} />
              <TextField select label="Participante" value={form.participant_id || ''} onChange={(event) => setForm((current) => ({ ...current, participant_id: Number(event.target.value) }))} required>{participants.map((participant) => <MenuItem key={participant.id} value={participant.id}>{participant.name}</MenuItem>)}</TextField>
              <TextField label="Cantidad" type="number" value={form.amount || ''} onChange={(event) => setForm((current) => ({ ...current, amount: Number(event.target.value) }))} required slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }} />
              <TextField
                select
                label="Moneda"
                value={form.currency}
                onChange={(event) => setForm((current) => ({ ...current, currency: event.target.value }))}
                required
                disabled={currenciesQuery.isPending || currenciesQuery.isError}
                error={currenciesQuery.isError}
                helperText={
                  currenciesQuery.isPending
                    ? 'Cargando monedas…'
                    : currenciesQuery.isError
                      ? 'No se pudieron cargar las monedas.'
                      : undefined
                }
              >
                {form.currency && !(currenciesQuery.data ?? []).some((currency) => currency.code === form.currency) && (
                  <MenuItem value={form.currency}>{form.currency}</MenuItem>
                )}
                {(currenciesQuery.data ?? []).map((currency) => (
                  <MenuItem key={currency.code} value={currency.code}>
                    {currency.code} — {currency.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField select label="Categoría" value={form.category} onChange={(event) => setForm((current) => ({ ...current, category: event.target.value as TripExpense['category'] }))}>{Object.entries(categories).map(([value, label]) => <MenuItem key={value} value={value}>{label}</MenuItem>)}</TextField>
              <TextField label="Fecha" type="date" value={form.expense_date} onChange={(event) => setForm((current) => ({ ...current, expense_date: event.target.value }))} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: tripStartDate, max: tripEndDate } }} />
            </Box>
          </DialogContent>
          <DialogActions><Button onClick={() => setFormOpen(false)} disabled={saveMutation.isPending}>Cancelar</Button><Button type="submit" variant="contained" disabled={saveMutation.isPending}>{saveMutation.isPending ? 'Guardando...' : 'Guardar gasto'}</Button></DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(toDelete)} onClose={() => !deleteMutation.isPending && setToDelete(null)} fullWidth maxWidth="xs">
        <DialogTitle>Eliminar gasto</DialogTitle>
        <DialogContent><DialogContentText>¿Quieres eliminar el gasto «{toDelete?.name}»?</DialogContentText></DialogContent>
        <DialogActions><Button onClick={() => setToDelete(null)} disabled={deleteMutation.isPending}>Cancelar</Button><Button color="error" variant="contained" disabled={deleteMutation.isPending} onClick={() => { if (toDelete) deleteMutation.mutate(toDelete.id) }}>{deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}</Button></DialogActions>
      </Dialog>
    </Paper>
  )
}
