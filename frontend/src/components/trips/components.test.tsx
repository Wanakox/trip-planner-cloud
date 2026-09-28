import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { AccommodationsManager } from './AccommodationsManager'
import { ActivitiesManager } from './ActivitiesManager'
import { ChecklistManager } from './ChecklistManager'
import { CurrencyConverter } from './CurrencyConverter'
import { DestinationsManager } from './DestinationsManager'
import { DocumentsManager } from './DocumentsManager'
import { ExpensesManager } from './ExpensesManager'
import { NotesManager } from './NotesManager'
import { ParticipantsManager } from './ParticipantsManager'
import { TransportsManager } from './TransportsManager'
import { TripCard } from './TripCard'

vi.mock('../../api/trips', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../api/trips')>()
  return {
    ...original,
    getExpenseSummary: vi.fn().mockResolvedValue({
      currency: 'EUR', budget: 1000, total_expenses: 0,
      remaining_budget: 1000, budget_exceeded: false, participants: [],
    }),
  }
})

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <MemoryRouter><QueryClientProvider client={client}>{children}</QueryClientProvider></MemoryRouter>
}

describe('componentes del detalle del viaje', () => {
  it('renderiza todas las secciones aunque estén vacías', () => {
    render(<>
      <ActivitiesManager tripId={1} totalDays={7} initialActivities={[]} />
      <ChecklistManager tripId={1} initialTasks={[]} />
      <DestinationsManager tripId={1} initialDestinations={[]} currencies={[{ code: 'EUR', name: 'Euro' }]} />
      <ParticipantsManager tripId={1} currency="EUR" expenses={[]} initialParticipants={[]} />
      <ExpensesManager tripId={1} tripStartDate="2026-09-01" tripEndDate="2026-09-07" tripCurrency="EUR" budget={1000} participants={[]} initialExpenses={[]} />
      <TransportsManager tripId={1} tripStartDate="2026-09-01" tripEndDate="2026-09-07" currency="EUR" initialTransports={[]} />
      <AccommodationsManager tripId={1} tripStartDate="2026-09-01" tripEndDate="2026-09-07" currency="EUR" initialAccommodations={[]} />
      <NotesManager tripId={1} totalDays={7} tripStatus="completed" tripStartDate="2026-09-01" initialNotes={[]} />
      <DocumentsManager tripId={1} tripCompleted initialFiles={[]} />
      <CurrencyConverter currencies={['EUR', 'USD']} />
    </>, { wrapper })
    expect(screen.getByText('Itinerario diario')).toBeInTheDocument()
    expect(screen.getByText('Checklist')).toBeInTheDocument()
    expect(screen.getByText('Participantes')).toBeInTheDocument()
    expect(screen.getByText('Gastos')).toBeInTheDocument()
    expect(screen.getByText('Transporte')).toBeInTheDocument()
    expect(screen.getByText('Alojamiento')).toBeInTheDocument()
    expect(screen.getByText('Notas')).toBeInTheDocument()
    expect(screen.getByText('Documentos')).toBeInTheDocument()
    expect(screen.getByText('Convertir moneda')).toBeInTheDocument()
  })

  it.each([
    ['planning', 'Planificando'],
    ['in_progress', 'En curso'],
    ['completed', 'Completado'],
    ['cancelled', 'Cancelado'],
  ])('muestra el estado %s y enlaza todo el viaje', (status, label) => {
    const trip = {
      id: 5, name: 'Creta', status, origin: 'Madrid', description: '',
      start_date: '2026-09-01', end_date: '2026-09-07', budget: 900,
      currency: 'EUR', destinations: [
        { id: 2, country: 'Grecia', city: 'Heraclión', currency: 'EUR', order: 2 },
        { id: 1, country: 'Grecia', city: 'Atenas', currency: 'EUR', order: 1 },
      ],
    }
    render(<TripCard trip={trip as never} />, { wrapper })
    expect(screen.getByText(label)).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('href', '/viajes/5')
    expect(screen.getByText('Atenas · Heraclión')).toBeInTheDocument()
  })
})
