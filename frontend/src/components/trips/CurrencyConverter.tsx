import CurrencyExchangeOutlinedIcon from '@mui/icons-material/CurrencyExchangeOutlined'
import SwapHorizOutlinedIcon from '@mui/icons-material/SwapHorizOutlined'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { convertCurrency, getCurrencies } from '../../api/currency'

function formatAmount(amount: string, currency: string) {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(Number(amount))
}

export function CurrencyConverter({ currencies }: { currencies: string[] }) {
  const [open, setOpen] = useState(false)
  const [amount, setAmount] = useState('1')
  const [fromCurrency, setFromCurrency] = useState(currencies[0] ?? 'EUR')
  const [toCurrency, setToCurrency] = useState(
    currencies.find((currency) => currency !== currencies[0]) ?? 'USD',
  )
  const currenciesQuery = useQuery({
    queryKey: ['currencies'],
    queryFn: getCurrencies,
    enabled: open,
  })
  const conversionMutation = useMutation({
    mutationFn: () => convertCurrency(Number(amount), fromCurrency, toCurrency),
  })

  const swapCurrencies = () => {
    setFromCurrency(toCurrency)
    setToCurrency(fromCurrency)
    conversionMutation.reset()
  }

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (Number(amount) > 0 && fromCurrency !== toCurrency) conversionMutation.mutate()
  }

  return (
    <>
      <Button
        size="small"
        variant="text"
        startIcon={<CurrencyExchangeOutlinedIcon />}
        onClick={() => { conversionMutation.reset(); setOpen(true) }}
      >
        Convertir moneda
      </Button>

      <Dialog open={open} onClose={() => !conversionMutation.isPending && setOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>Conversor de moneda</DialogTitle>
          <DialogContent>
            <Typography sx={{ mb: 2.5, color: 'text.secondary', fontSize: 13 }}>
              Convierte importes utilizando el tipo de cambio más reciente disponible.
            </Typography>

            {currenciesQuery.isError && <Alert severity="error">No se ha podido cargar la lista de monedas.</Alert>}
            {currenciesQuery.isLoading
              ? <Box sx={{ minHeight: 150, display: 'grid', placeItems: 'center' }}><CircularProgress size={28} /></Box>
              : <Stack spacing={2}>
                  <TextField
                    label="Cantidad"
                    type="number"
                    value={amount}
                    onChange={(event) => { setAmount(event.target.value); conversionMutation.reset() }}
                    required
                    slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
                  />
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ alignItems: 'center' }}>
                    <TextField select fullWidth label="De" value={fromCurrency} onChange={(event) => { setFromCurrency(event.target.value); conversionMutation.reset() }}>
                      {(currenciesQuery.data ?? []).map((currency) => <MenuItem key={currency.code} value={currency.code}>{currency.code} — {currency.name}</MenuItem>)}
                    </TextField>
                    <IconButton aria-label="Intercambiar monedas" onClick={swapCurrencies}><SwapHorizOutlinedIcon /></IconButton>
                    <TextField select fullWidth label="A" value={toCurrency} onChange={(event) => { setToCurrency(event.target.value); conversionMutation.reset() }}>
                      {(currenciesQuery.data ?? []).map((currency) => <MenuItem key={currency.code} value={currency.code}>{currency.code} — {currency.name}</MenuItem>)}
                    </TextField>
                  </Stack>
                </Stack>}

            {fromCurrency === toCurrency && <Alert severity="warning" sx={{ mt: 2 }}>Selecciona dos monedas diferentes.</Alert>}
            {conversionMutation.isError && <Alert severity="error" sx={{ mt: 2 }}>No se ha podido realizar la conversión. Inténtalo de nuevo.</Alert>}
            {conversionMutation.data && (
              <Box sx={{ mt: 2.5, p: 2.25, borderRadius: '14px', bgcolor: 'primary.light' }}>
                <Typography sx={{ color: 'text.secondary', fontSize: 13 }}>
                  {formatAmount(conversionMutation.data.amount, conversionMutation.data.from_currency)} equivale a
                </Typography>
                <Typography sx={{ mt: 0.25, color: 'primary.main', fontSize: 28, fontWeight: 850 }}>
                  {formatAmount(conversionMutation.data.result, conversionMutation.data.to_currency)}
                </Typography>
                <Typography sx={{ mt: 0.75, color: 'text.secondary', fontSize: 12 }}>
                  1 {conversionMutation.data.from_currency} = {Number(conversionMutation.data.rate).toLocaleString('es-ES', { maximumFractionDigits: 6 })} {conversionMutation.data.to_currency}
                  {conversionMutation.data.rate_date !== 'same-currency' && ` · Tipo del ${conversionMutation.data.rate_date}`}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)} disabled={conversionMutation.isPending}>Cerrar</Button>
            <Button type="submit" variant="contained" disabled={currenciesQuery.isLoading || currenciesQuery.isError || conversionMutation.isPending || Number(amount) <= 0 || fromCurrency === toCurrency}>
              {conversionMutation.isPending ? 'Convirtiendo...' : 'Convertir'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </>
  )
}
