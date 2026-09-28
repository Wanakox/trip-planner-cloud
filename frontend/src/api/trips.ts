import type {
  Trip,
  TripAccommodation,
  AccommodationPayload,
  TripActivity,
  TripCreatePayload,
  TripDetails,
  DestinationCreatePayload,
  DestinationOrderPayload,
  ActivityOrderPayload,
  ActivityPayload,
  TripExpense,
  ExpensePayload,
  ExpenseSummary,
  TripParticipant,
  TripNote,
  TripFile,
  TripTask,
  TaskOrderPayload,
  TaskPayload,
  TripTransport,
  TripUpdatePayload,
  TransportPayload,
  ParticipantPayload,
  NotePayload,
} from '../types/trip'
import { httpClient } from './http'

export async function getTrips(): Promise<Trip[]> {
  const { data } =
    await httpClient.get<Trip[]>('/trips')

  return data
}

export async function createTrip(
  payload: TripCreatePayload,
): Promise<Trip> {
  const { data } =
    await httpClient.post<Trip>(
      '/trips',
      payload,
    )

  return data
}

export async function getTrip(
  tripId: number,
): Promise<Trip> {
  const { data } =
    await httpClient.get<Trip>(`/trips/${tripId}`)

  return data
}

export async function updateTrip(
  tripId: number,
  payload: TripUpdatePayload,
): Promise<Trip> {
  const { data } =
    await httpClient.patch<Trip>(
      `/trips/${tripId}`,
      payload,
    )

  return data
}

export async function rateTrip(
  tripId: number,
  rating: number,
): Promise<Trip> {
  const { data } =
    await httpClient.put<Trip>(
      `/trips/${tripId}/rating`,
      { rating },
    )

  return data
}

export async function deleteTrip(
  tripId: number,
): Promise<void> {
  await httpClient.delete(`/trips/${tripId}`)
}

export async function addDestination(
  tripId: number,
  payload: DestinationCreatePayload,
): Promise<Trip> {
  const { data } = await httpClient.post<Trip>(
    `/trips/${tripId}/destinations`,
    payload,
  )
  return data
}

export async function updateDestination(
  tripId: number,
  destinationId: number,
  payload: DestinationCreatePayload,
): Promise<Trip> {
  const { data } = await httpClient.patch<Trip>(
    `/trips/${tripId}/destinations/${destinationId}`,
    payload,
  )
  return data
}

export async function deleteDestination(
  tripId: number,
  destinationId: number,
): Promise<Trip> {
  const { data } = await httpClient.delete<Trip>(
    `/trips/${tripId}/destinations/${destinationId}`,
  )
  return data
}

export async function reorderDestinations(
  tripId: number,
  payload: DestinationOrderPayload,
): Promise<Trip> {
  const { data } = await httpClient.put<Trip>(
    `/trips/${tripId}/destinations/order`,
    payload,
  )
  return data
}

export async function addActivity(
  tripId: number,
  payload: ActivityPayload,
): Promise<TripActivity> {
  const { data } = await httpClient.post<TripActivity>(
    `/trips/${tripId}/activities`,
    payload,
  )
  return data
}

export async function getTripActivities(
  tripId: number,
): Promise<TripActivity[]> {
  const { data } = await httpClient.get<TripActivity[]>(
    `/trips/${tripId}/activities`,
  )
  return data
}

export async function updateActivity(
  tripId: number,
  activityId: number,
  payload: ActivityPayload,
): Promise<TripActivity> {
  const { data } = await httpClient.patch<TripActivity>(
    `/trips/${tripId}/activities/${activityId}`,
    payload,
  )
  return data
}

export async function deleteActivity(
  tripId: number,
  activityId: number,
): Promise<void> {
  await httpClient.delete(
    `/trips/${tripId}/activities/${activityId}`,
  )
}

export async function setActivityCompleted(
  tripId: number,
  activityId: number,
  completed: boolean,
): Promise<TripActivity> {
  const { data } = await httpClient.put<TripActivity>(
    `/trips/${tripId}/activities/${activityId}/completed`,
    { completed },
  )
  return data
}

export async function reorderActivities(
  tripId: number,
  payload: ActivityOrderPayload,
): Promise<TripActivity[]> {
  const { data } = await httpClient.put<TripActivity[]>(
    `/trips/${tripId}/activities/order`,
    payload,
  )
  return data
}

export async function getTripTasks(tripId: number): Promise<TripTask[]> {
  const { data } = await httpClient.get<TripTask[]>(`/trips/${tripId}/checklist`)
  return data
}

export async function addTask(
  tripId: number,
  payload: TaskPayload,
): Promise<TripTask> {
  const { data } = await httpClient.post<TripTask>(`/trips/${tripId}/tasks`, payload)
  return data
}

export async function updateTask(
  tripId: number,
  taskId: number,
  payload: TaskPayload,
): Promise<TripTask> {
  const { data } = await httpClient.patch<TripTask>(
    `/trips/${tripId}/tasks/${taskId}`,
    payload,
  )
  return data
}

export async function deleteTask(tripId: number, taskId: number): Promise<void> {
  await httpClient.delete(`/trips/${tripId}/tasks/${taskId}`)
}

export async function setTaskCompleted(
  tripId: number,
  taskId: number,
  completed: boolean,
): Promise<TripTask> {
  const { data } = await httpClient.put<TripTask>(
    `/trips/${tripId}/tasks/${taskId}/completed`,
    { completed },
  )
  return data
}

export async function reorderTasks(
  tripId: number,
  payload: TaskOrderPayload,
): Promise<TripTask[]> {
  const { data } = await httpClient.put<TripTask[]>(
    `/trips/${tripId}/tasks/order`,
    payload,
  )
  return data
}

export async function getTripParticipants(tripId: number): Promise<TripParticipant[]> {
  const { data } = await httpClient.get<TripParticipant[]>(`/trips/${tripId}/participants`)
  return data
}

export async function getTripExpenses(tripId: number): Promise<TripExpense[]> {
  const { data } = await httpClient.get<TripExpense[]>(`/trips/${tripId}/expenses`)
  return data
}

export async function getExpenseSummary(tripId: number): Promise<ExpenseSummary> {
  const { data } = await httpClient.get<ExpenseSummary>(`/trips/${tripId}/expenses/summary`)
  return data
}

export async function addExpense(
  tripId: number,
  payload: ExpensePayload,
): Promise<TripExpense> {
  const { data } = await httpClient.post<TripExpense>(`/trips/${tripId}/expenses`, payload)
  return data
}

export async function updateExpense(
  tripId: number,
  expenseId: number,
  payload: ExpensePayload,
): Promise<TripExpense> {
  const { data } = await httpClient.patch<TripExpense>(
    `/trips/${tripId}/expenses/${expenseId}`,
    payload,
  )
  return data
}

export async function deleteExpense(tripId: number, expenseId: number): Promise<void> {
  await httpClient.delete(`/trips/${tripId}/expenses/${expenseId}`)
}

export async function getTripNotes(tripId: number): Promise<TripNote[]> {
  const { data } = await httpClient.get<TripNote[]>(`/trips/${tripId}/notes`)
  return data
}

export async function addNote(tripId: number, payload: NotePayload): Promise<TripNote> {
  const { data } = await httpClient.post<TripNote>(`/trips/${tripId}/notes`, payload)
  return data
}

export async function updateNote(
  tripId: number,
  noteId: number,
  payload: NotePayload,
): Promise<TripNote> {
  const { data } = await httpClient.patch<TripNote>(
    `/trips/${tripId}/notes/${noteId}`,
    payload,
  )
  return data
}

export async function deleteNote(tripId: number, noteId: number): Promise<void> {
  await httpClient.delete(`/trips/${tripId}/notes/${noteId}`)
}

export async function getTripFiles(tripId: number): Promise<TripFile[]> {
  const { data } = await httpClient.get<TripFile[]>(`/trips/${tripId}/files`)
  return data
}

export async function uploadTripFiles(
  tripId: number,
  files: File[],
): Promise<TripFile[]> {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  const { data } = await httpClient.post<TripFile[]>(
    `/trips/${tripId}/files`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function deleteTripFile(tripId: number, fileId: number): Promise<void> {
  await httpClient.delete(`/trips/${tripId}/files/${fileId}`)
}

export async function addParticipant(
  tripId: number,
  payload: ParticipantPayload,
): Promise<TripParticipant> {
  const { data } = await httpClient.post<TripParticipant>(`/trips/${tripId}/participants`, payload)
  return data
}

export async function updateParticipant(
  tripId: number,
  participantId: number,
  payload: ParticipantPayload,
): Promise<TripParticipant> {
  const { data } = await httpClient.patch<TripParticipant>(
    `/trips/${tripId}/participants/${participantId}`,
    payload,
  )
  return data
}

export async function deleteParticipant(
  tripId: number,
  participantId: number,
): Promise<void> {
  await httpClient.delete(`/trips/${tripId}/participants/${participantId}`)
}

export async function getTripTransports(
  tripId: number,
): Promise<TripTransport[]> {
  const { data } = await httpClient.get<TripTransport[]>(
    `/trips/${tripId}/transports`,
  )
  return data
}

export async function addTransport(
  tripId: number,
  payload: TransportPayload,
): Promise<TripTransport> {
  const { data } = await httpClient.post<TripTransport>(
    `/trips/${tripId}/transports`,
    payload,
  )
  return data
}

export async function updateTransport(
  tripId: number,
  transportId: number,
  payload: TransportPayload,
): Promise<TripTransport> {
  const { data } = await httpClient.patch<TripTransport>(
    `/trips/${tripId}/transports/${transportId}`,
    payload,
  )
  return data
}

export async function deleteTransport(
  tripId: number,
  transportId: number,
): Promise<void> {
  await httpClient.delete(
    `/trips/${tripId}/transports/${transportId}`,
  )
}

export async function getTripAccommodations(
  tripId: number,
): Promise<TripAccommodation[]> {
  const { data } = await httpClient.get<TripAccommodation[]>(
    `/trips/${tripId}/accommodations`,
  )
  return data
}

export async function addAccommodation(
  tripId: number,
  payload: AccommodationPayload,
): Promise<TripAccommodation> {
  const { data } = await httpClient.post<TripAccommodation>(
    `/trips/${tripId}/accommodations`,
    payload,
  )
  return data
}

export async function updateAccommodation(
  tripId: number,
  accommodationId: number,
  payload: AccommodationPayload,
): Promise<TripAccommodation> {
  const { data } = await httpClient.patch<TripAccommodation>(
    `/trips/${tripId}/accommodations/${accommodationId}`,
    payload,
  )
  return data
}

export async function deleteAccommodation(
  tripId: number,
  accommodationId: number,
): Promise<void> {
  await httpClient.delete(
    `/trips/${tripId}/accommodations/${accommodationId}`,
  )
}

export async function getTripDetails(
  tripId: number,
): Promise<TripDetails> {
  const baseUrl = `/trips/${tripId}`
  const { data: trip } =
    await httpClient.get<Trip>(baseUrl)

  async function getOptionalList<T>(
    url: string,
  ): Promise<T[]> {
    try {
      const { data } =
        await httpClient.get<T[]>(url)
      return data
    } catch {
      return []
    }
  }

  const [
    activities,
    tasks,
    expenses,
    participants,
    transports,
    accommodations,
    notes,
    files,
  ] = await Promise.all([
    getOptionalList<TripActivity>(
      `${baseUrl}/activities`,
    ),
    getOptionalList<TripTask>(
      `${baseUrl}/checklist`,
    ),
    getOptionalList<TripExpense>(
      `${baseUrl}/expenses`,
    ),
    getOptionalList<TripParticipant>(
      `${baseUrl}/participants`,
    ),
    getOptionalList<TripTransport>(
      `${baseUrl}/transports`,
    ),
    getOptionalList<TripAccommodation>(
      `${baseUrl}/accommodations`,
    ),
    trip.status === 'completed' || trip.status === 'in_progress'
      ? getOptionalList<TripNote>(`${baseUrl}/notes`)
      : Promise.resolve([]),
    trip.status === 'completed'
      ? getOptionalList<TripFile>(
          `${baseUrl}/files`,
        )
      : Promise.resolve([]),
  ])

  return {
    trip,
    activities,
    tasks,
    expenses,
    participants,
    transports,
    accommodations,
    notes,
    files,
  }
}

export async function downloadTripExport(
  tripId: number,
): Promise<Blob> {
  const { data } = await httpClient.get<Blob>(
    `/trips/${tripId}/export`,
    { responseType: 'blob' },
  )

  return data
}

export async function getTripFileContent(
  tripId: number,
  fileId: number,
): Promise<Blob> {
  const { data } = await httpClient.get<Blob>(
    `/trips/${tripId}/files/${fileId}/content`,
    {
      responseType: 'blob',
    },
  )
  return data
}
