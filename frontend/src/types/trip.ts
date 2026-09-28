export type TripStatus =
  | 'planning'
  | 'in_progress'
  | 'completed'
  | 'cancelled'

export type Destination = {
  id: number
  country: string
  city: string
  currency: string
  order: number
}

export type Trip = {
  id: number
  user_id: number
  name: string
  origin: string
  description: string | null
  start_date: string
  end_date: string
  total_days: number
  budget: string
  currency: string
  status: TripStatus
  rating: number | null
  destinations: Destination[]
}

export type DestinationCreatePayload = {
  country: string
  city: string
  currency: string
}

export type DestinationOrderPayload = {
  destinations: Array<{
    id: number
    order: number
  }>
}

export type TripCreatePayload = {
  name: string
  origin: string
  description: string | null
  start_date: string
  end_date: string
  budget: number
  destinations: DestinationCreatePayload[]
}

export type TripUpdatePayload = {
  name: string
  origin: string
  description: string | null
  start_date: string
  end_date: string
  budget: number
  currency: string
  status: TripStatus
}

export type TripActivity = {
  id: number
  trip_id: number
  name: string
  location: string | null
  start_time: string | null
  day_number: number
  completed: boolean
  order: number
}

export type ActivityPayload = {
  name: string
  location: string | null
  start_time: string | null
  day_number: number
}

export type ActivityOrderPayload = {
  activities: Array<{
    id: number
    day_number: number
    order: number
  }>
}

export type TripTask = {
  id: number
  trip_id: number
  name: string
  priority: 'low' | 'medium' | 'high'
  completed: boolean
  order: number
}

export type TaskPayload = {
  name: string
  priority: TripTask['priority']
}

export type TaskOrderPayload = {
  tasks: Array<{
    id: number
    order: number
  }>
}

export type TripExpense = {
  id: number
  trip_id: number
  participant_id: number
  name: string
  amount: string
  category:
    | 'accommodation'
    | 'transport'
    | 'food'
    | 'leisure'
    | 'shopping'
    | 'other'
  currency: string
  expense_date: string
}

export type ExpensePayload = {
  participant_id: number
  name: string
  amount: number
  category: TripExpense['category']
  currency: string
  expense_date: string
}

export type ExpenseSummary = {
  currency: string
  budget: string | null
  total_expenses: string
  remaining_budget: string | null
  budget_exceeded: boolean | null
  participants: Array<{
    participant_id: number
    participant_name: string
    total_expenses: string
  }>
}

export type TripParticipant = {
  id: number
  trip_id: number
  name: string
}

export type ParticipantPayload = {
  name: string
}

export type TripTransport = {
  id: number
  trip_id: number
  transport_type:
    | 'flight'
    | 'train'
    | 'bus'
    | 'car'
    | 'boat'
    | 'other'
  price: string | null
  departure_date: string
  arrival_date: string | null
  departure_time: string | null
  arrival_time: string | null
  origin: string
  destination: string
  check_in_date: string | null
}

export type TransportPayload = {
  transport_type: TripTransport['transport_type']
  price: number | null
  departure_date: string
  arrival_date: string | null
  departure_time: string | null
  arrival_time: string | null
  origin: string
  destination: string
  check_in_date: string | null
}

export type TripAccommodation = {
  id: number
  trip_id: number
  name: string
  address: string
  price: string | null
  check_in_date: string
  check_out_date: string
  check_in_time: string | null
  check_out_time: string | null
}

export type AccommodationPayload = {
  name: string
  address: string
  price: number | null
  check_in_date: string
  check_out_date: string
  check_in_time: string | null
  check_out_time: string | null
}

export type TripFile = {
  id: number
  trip_id: number
  name: string
  extension: string
  size: number
}

export type TripNote = {
  id: number
  trip_id: number
  title: string
  text: string
  day_number: number | null
}

export type NotePayload = {
  title: string
  text: string
  day_number: number
}

export type TripDetails = {
  trip: Trip
  activities: TripActivity[]
  tasks: TripTask[]
  expenses: TripExpense[]
  participants: TripParticipant[]
  transports: TripTransport[]
  accommodations: TripAccommodation[]
  notes: TripNote[]
  files: TripFile[]
}
