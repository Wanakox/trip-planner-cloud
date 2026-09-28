import { beforeEach, describe, expect, it, vi } from 'vitest'

import { httpClient } from './http'
import * as trips from './trips'

describe('API de viajes', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.spyOn(httpClient, 'get').mockResolvedValue({ data: [] })
    vi.spyOn(httpClient, 'post').mockResolvedValue({ data: {} })
    vi.spyOn(httpClient, 'patch').mockResolvedValue({ data: {} })
    vi.spyOn(httpClient, 'put').mockResolvedValue({ data: {} })
    vi.spyOn(httpClient, 'delete').mockResolvedValue({ data: {} })
  })

  it('cubre el CRUD principal del viaje', async () => {
    await trips.getTrips(); expect(httpClient.get).toHaveBeenCalledWith('/trips')
    await trips.getTrip(4); expect(httpClient.get).toHaveBeenCalledWith('/trips/4')
    await trips.createTrip({ name: 'Viaje' } as never); expect(httpClient.post).toHaveBeenCalledWith('/trips', { name: 'Viaje' })
    await trips.updateTrip(4, { name: 'Otro' } as never); expect(httpClient.patch).toHaveBeenCalledWith('/trips/4', { name: 'Otro' })
    await trips.rateTrip(4, 5); expect(httpClient.put).toHaveBeenCalledWith('/trips/4/rating', { rating: 5 })
    await trips.deleteTrip(4); expect(httpClient.delete).toHaveBeenCalledWith('/trips/4')
  })

  it.each([
    ['destino', () => trips.addDestination(2, { city: 'Roma' } as never), 'post', '/trips/2/destinations'],
    ['actividad', () => trips.addActivity(2, { name: 'Museo' } as never), 'post', '/trips/2/activities'],
    ['tarea', () => trips.addTask(2, { title: 'Pasaporte' } as never), 'post', '/trips/2/tasks'],
    ['participante', () => trips.addParticipant(2, { name: 'Ana' } as never), 'post', '/trips/2/participants'],
    ['gasto', () => trips.addExpense(2, { description: 'Cena' } as never), 'post', '/trips/2/expenses'],
    ['nota', () => trips.addNote(2, { title: 'Día 1' } as never), 'post', '/trips/2/notes'],
    ['transporte', () => trips.addTransport(2, { company: 'Renfe' } as never), 'post', '/trips/2/transports'],
    ['alojamiento', () => trips.addAccommodation(2, { name: 'Hotel' } as never), 'post', '/trips/2/accommodations'],
  ])('añade %s en la ruta esperada', async (_name, action, method, url) => {
    await action()
    expect(httpClient[method as 'post']).toHaveBeenCalledWith(url, expect.anything())
  })

  it('cubre completar y reordenar actividades y tareas', async () => {
    await trips.setActivityCompleted(3, 8, true)
    expect(httpClient.put).toHaveBeenCalledWith('/trips/3/activities/8/completed', { completed: true })
    await trips.reorderActivities(3, { activities: [] } as never)
    expect(httpClient.put).toHaveBeenCalledWith('/trips/3/activities/order', { activities: [] })
    await trips.setTaskCompleted(3, 7, false)
    expect(httpClient.put).toHaveBeenCalledWith('/trips/3/tasks/7/completed', { completed: false })
    await trips.reorderTasks(3, { tasks: [] } as never)
    expect(httpClient.put).toHaveBeenCalledWith('/trips/3/tasks/order', { tasks: [] })
  })

  it('construye el detalle y tolera el fallo de secciones opcionales', async () => {
    vi.mocked(httpClient.get).mockImplementation(async (url) => {
      if (url === '/trips/9') return { data: { id: 9, status: 'completed' } } as never
      if (url === '/trips/9/activities') throw new Error('fallo')
      return { data: [] } as never
    })
    const result = await trips.getTripDetails(9)
    expect(result.trip.id).toBe(9)
    expect(result.activities).toEqual([])
    expect(httpClient.get).toHaveBeenCalledWith('/trips/9/files')
    expect(httpClient.get).toHaveBeenCalledWith('/trips/9/notes')
  })

  it('no solicita notas ni documentos para un viaje futuro', async () => {
    vi.mocked(httpClient.get).mockImplementation(async (url) => ({ data: url === '/trips/10' ? { id: 10, status: 'upcoming' } : [] }) as never)
    await trips.getTripDetails(10)
    expect(httpClient.get).not.toHaveBeenCalledWith('/trips/10/notes')
    expect(httpClient.get).not.toHaveBeenCalledWith('/trips/10/files')
  })

  it('sube varios documentos en un FormData', async () => {
    const files = [new File(['a'], 'a.pdf'), new File(['b'], 'b.pdf')]
    await trips.uploadTripFiles(6, files)
    const call = vi.mocked(httpClient.post).mock.calls.at(-1)
    expect(call?.[0]).toBe('/trips/6/files')
    expect((call?.[1] as FormData).getAll('files')).toEqual(files)
  })
})
