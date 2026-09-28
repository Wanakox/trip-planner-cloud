import AirplanemodeActiveOutlinedIcon from '@mui/icons-material/AirplanemodeActiveOutlined'
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined'
import SwapHorizOutlinedIcon from '@mui/icons-material/SwapHorizOutlined'
import { Alert, Avatar, Box, Button, Chip, CircularProgress, Divider, IconButton, MenuItem, Paper, Stack, TextField, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'

import { searchFlights } from '../api/flights'
import type { CabinClass, FlightOffer, FlightSearchParams, FlightSlice } from '../api/flights'

const cabinLabels: Record<CabinClass, string> = { economy: 'Turista', premium_economy: 'Turista prémium', business: 'Business', first: 'Primera clase' }

function isoDate(offset: number) { const date = new Date(); date.setDate(date.getDate() + offset); return date.toISOString().slice(0, 10) }
function time(value: string) { return new Intl.DateTimeFormat('es-ES', { hour: '2-digit', minute: '2-digit' }).format(new Date(value)) }
function day(value: string) { return new Intl.DateTimeFormat('es-ES', { weekday: 'short', day: '2-digit', month: 'short' }).format(new Date(value)) }
function duration(value: string | null) {
  const match = value?.match(/PT(?:(\d+)H)?(?:(\d+)M)?/)
  return match ? [match[1] && `${match[1]} h`, match[2] && `${match[2]} min`].filter(Boolean).join(' ') : 'Duración no disponible'
}
function errorMessage(error: unknown) {
  if (!axios.isAxiosError(error) || !error.response) return 'No se puede conectar con el servicio de vuelos.'
  if (error.response.status === 503) return 'El proveedor de vuelos no está disponible temporalmente.'
  const detail = error.response.data?.detail
  if (detail === 'Origin and destination must be different') return 'El origen y el destino deben ser diferentes.'
  if (detail === 'Departure date cannot be in the past') return 'La salida no puede estar en el pasado.'
  if (detail === 'Return date cannot be before departure date') return 'La vuelta no puede ser anterior a la salida.'
  return 'No se ha podido completar la búsqueda. Revisa los datos.'
}

function SliceRow({ slice }: { slice: FlightSlice }) {
  const first = slice.segments[0]
  const last = slice.segments.at(-1)
  if (!first || !last) return <Alert severity="warning">Itinerario no disponible.</Alert>
  return <Box>
    <Typography sx={{ mb: 1, color: 'text.secondary', fontSize: 12, fontWeight: 700, textTransform: 'uppercase' }}>{day(first.departure)} · {slice.origin} → {slice.destination}</Typography>
    <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
      <Box><Typography sx={{ fontSize: 20, fontWeight: 850 }}>{time(first.departure)}</Typography><Typography color="text.secondary" sx={{ fontSize: 13 }}>{slice.origin}</Typography></Box>
      <Box sx={{ flex: 1, textAlign: 'center' }}><Typography color="text.secondary" sx={{ fontSize: 12 }}>{duration(slice.duration)}</Typography><Divider sx={{ my: .7 }} /><Typography sx={{ color: slice.stops ? 'warning.main' : 'success.main', fontSize: 12, fontWeight: 700 }}>{slice.stops ? `${slice.stops} ${slice.stops === 1 ? 'escala' : 'escalas'}` : 'Directo'}</Typography></Box>
      <Box sx={{ textAlign: 'right' }}><Typography sx={{ fontSize: 20, fontWeight: 850 }}>{time(last.arrival)}</Typography><Typography color="text.secondary" sx={{ fontSize: 13 }}>{slice.destination}</Typography></Box>
    </Stack>
    {slice.segments.length > 1 && <Typography color="text.secondary" sx={{ mt: 1, fontSize: 11 }}>Trayecto: {slice.segments.map((segment) => `${segment.origin}-${segment.destination}`).join(' · ')}</Typography>}
  </Box>
}

function OfferCard({ offer, cabin }: { offer: FlightOffer; cabin: CabinClass }) {
  return <Paper variant="outlined" sx={{ p: { xs: 2, md: 2.5 }, borderRadius: '18px', borderColor: '#dce3ec' }}>
    <Stack direction={{ xs: 'column', md: 'row' }} spacing={2.5}>
      <Stack spacing={2.25} divider={<Divider flexItem />} sx={{ flex: 1 }}>{offer.slices.map((slice, index) => <SliceRow key={`${offer.id}-${index}`} slice={slice} />)}</Stack>
      <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
      <Stack sx={{ minWidth: 190, justifyContent: 'space-between', alignItems: { md: 'flex-end' } }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}><Avatar sx={{ width: 34, height: 34, bgcolor: 'primary.light', color: 'primary.main', fontSize: 12, fontWeight: 800 }}>{offer.airline_code ?? offer.airline.slice(0, 2).toUpperCase()}</Avatar><Box><Typography sx={{ fontSize: 13, fontWeight: 750 }}>{offer.airline}</Typography><Typography color="text.secondary" sx={{ fontSize: 11 }}>{cabinLabels[cabin]}</Typography></Box></Stack>
        <Box sx={{ mt: 3, textAlign: { md: 'right' } }}><Typography color="text.secondary" sx={{ fontSize: 11 }}>Precio total</Typography><Typography sx={{ fontSize: 27, fontWeight: 900 }}>{new Intl.NumberFormat('es-ES', { style: 'currency', currency: offer.currency }).format(Number(offer.price))}</Typography><Typography color="text.secondary" sx={{ fontSize: 11 }}>para todos los pasajeros</Typography></Box>
      </Stack>
    </Stack>
  </Paper>
}

export function FlightSearchPage() {
  const [roundTrip, setRoundTrip] = useState(true)
  const [visibleOffers, setVisibleOffers] = useState(10)
  const [form, setForm] = useState<FlightSearchParams>({ origin: '', destination: '', departure_date: isoDate(1), return_date: isoDate(8), adults: 1, cabin_class: 'economy' })
  const mutation = useMutation({ mutationFn: searchFlights })
  const submit = (event: React.FormEvent<HTMLFormElement>) => { event.preventDefault(); setVisibleOffers(10); mutation.mutate({ ...form, origin: form.origin.trim().toUpperCase(), destination: form.destination.trim().toUpperCase(), return_date: roundTrip ? form.return_date : undefined }) }
  const swap = () => { setForm((current) => ({ ...current, origin: current.destination, destination: current.origin })); mutation.reset() }

  return <Box component="main" sx={{ minHeight: '100dvh', px: { xs: 2, sm: 3, md: 5, lg: 6 }, pt: { xs: 10, md: 5 }, pb: 5 }}><Box sx={{ maxWidth: 1400, mx: 'auto' }}>
    <Typography component="h1" sx={{ fontSize: { xs: 32, md: 38 }, fontWeight: 850, letterSpacing: -.8 }}>Buscar vuelos</Typography>
    <Typography color="text.secondary" sx={{ mt: 1 }}>Consulta vuelos para preparar tu próximo viaje.</Typography>
    <Alert severity="info" sx={{ mt: 2.5 }}>Entorno de demostración: los vuelos, horarios y precios proceden del modo de prueba de Duffel y pueden no representar ofertas reales.</Alert>
    <Paper component="form" onSubmit={submit} variant="outlined" sx={{ mt: 3.5, p: { xs: 2, md: 3 }, borderRadius: '20px', borderColor: '#dce3ec' }}>
      <Stack direction="row" spacing={1} sx={{ mb: 2.5 }}><Button size="small" variant={roundTrip ? 'contained' : 'text'} onClick={() => setRoundTrip(true)}>Ida y vuelta</Button><Button size="small" variant={!roundTrip ? 'contained' : 'text'} onClick={() => { setRoundTrip(false); mutation.reset() }}>Solo ida</Button></Stack>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr auto 1fr 1fr 1fr', xl: '1fr auto 1fr 1fr 1fr .65fr .85fr' }, gap: 1.5, alignItems: 'start' }}>
        <TextField label="Origen" value={form.origin} onChange={(event) => setForm((current) => ({ ...current, origin: event.target.value.toUpperCase().slice(0, 3) }))} required helperText="Código IATA, por ejemplo MAD" slotProps={{ htmlInput: { minLength: 3, maxLength: 3 } }} />
        <IconButton aria-label="Intercambiar aeropuertos" onClick={swap} sx={{ mt: 1 }}><SwapHorizOutlinedIcon /></IconButton>
        <TextField label="Destino" value={form.destination} onChange={(event) => setForm((current) => ({ ...current, destination: event.target.value.toUpperCase().slice(0, 3) }))} required helperText="Código IATA, por ejemplo HER" slotProps={{ htmlInput: { minLength: 3, maxLength: 3 } }} />
        <TextField label="Salida" type="date" value={form.departure_date} onChange={(event) => setForm((current) => ({ ...current, departure_date: event.target.value }))} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: isoDate(0) } }} />
        {roundTrip && <TextField label="Vuelta" type="date" value={form.return_date ?? ''} onChange={(event) => setForm((current) => ({ ...current, return_date: event.target.value }))} required slotProps={{ inputLabel: { shrink: true }, htmlInput: { min: form.departure_date } }} />}
        <TextField select label="Adultos" value={form.adults} onChange={(event) => setForm((current) => ({ ...current, adults: Number(event.target.value) }))}>{Array.from({ length: 9 }, (_, index) => index + 1).map((value) => <MenuItem key={value} value={value}>{value}</MenuItem>)}</TextField>
        <TextField select label="Clase" value={form.cabin_class} onChange={(event) => setForm((current) => ({ ...current, cabin_class: event.target.value as CabinClass }))}>{Object.entries(cabinLabels).map(([value, label]) => <MenuItem key={value} value={value}>{label}</MenuItem>)}</TextField>
      </Box>
      <Stack direction="row" sx={{ mt: 2.5, justifyContent: 'flex-end' }}><Button type="submit" variant="contained" size="large" startIcon={mutation.isPending ? <CircularProgress size={18} color="inherit" /> : <SearchOutlinedIcon />} disabled={mutation.isPending}>{mutation.isPending ? 'Buscando...' : 'Buscar vuelos'}</Button></Stack>
    </Paper>
    {mutation.isError && <Alert severity="error" sx={{ mt: 3 }}>{errorMessage(mutation.error)}</Alert>}
    {mutation.data && <Box sx={{ mt: 4 }}><Stack direction={{ xs: 'column', sm: 'row' }} sx={{ mb: 2, gap: 1, justifyContent: 'space-between' }}><Box><Typography component="h2" sx={{ fontSize: 22, fontWeight: 850 }}>{mutation.data.origin} → {mutation.data.destination}</Typography><Typography color="text.secondary" sx={{ fontSize: 13 }}>{mutation.data.offers.length} resultados · {mutation.data.adults} {mutation.data.adults === 1 ? 'adulto' : 'adultos'} · {cabinLabels[mutation.data.cabin_class]}</Typography></Box><Chip label="Ordenados por precio" variant="outlined" /></Stack>
      {mutation.data.offers.length ? <Stack spacing={2}>
        {mutation.data.offers.slice(0, visibleOffers).map((offer) => <OfferCard key={offer.id} offer={offer} cabin={mutation.data.cabin_class} />)}
        {visibleOffers < mutation.data.offers.length && <Button variant="outlined" size="large" onClick={() => setVisibleOffers((current) => current + 10)} sx={{ alignSelf: 'center', minWidth: 220 }}>Mostrar 10 más</Button>}
        <Typography color="text.secondary" sx={{ textAlign: 'center', fontSize: 12 }}>Mostrando {Math.min(visibleOffers, mutation.data.offers.length)} de {mutation.data.offers.length} ofertas</Typography>
      </Stack> : <Paper variant="outlined" sx={{ p: 5, textAlign: 'center', borderRadius: '18px' }}><AirplanemodeActiveOutlinedIcon sx={{ fontSize: 42, color: 'text.secondary' }} /><Typography sx={{ mt: 1, fontWeight: 750 }}>No se han encontrado vuelos</Typography><Typography color="text.secondary" sx={{ fontSize: 13 }}>Prueba con otras fechas o aeropuertos.</Typography></Paper>}
    </Box>}
  </Box></Box>
}
