import { httpClient } from './http'

export type CabinClass = 'economy' | 'premium_economy' | 'business' | 'first'

export type FlightSegment = { origin: string; destination: string; departure: string; arrival: string; airline: string; airline_code: string | null; flight_number: string | null }
export type FlightSlice = { origin: string; destination: string; duration: string | null; stops: number; segments: FlightSegment[] }
export type FlightOffer = { id: string; airline: string; airline_code: string | null; price: string; currency: string; expires_at: string | null; slices: FlightSlice[] }
export type FlightSearch = { origin: string; destination: string; departure_date: string; return_date: string | null; adults: number; cabin_class: CabinClass; offers: FlightOffer[] }
export type FlightSearchParams = { origin: string; destination: string; departure_date: string; return_date?: string; adults: number; cabin_class: CabinClass }

export async function searchFlights(params: FlightSearchParams): Promise<FlightSearch> {
  const { data } = await httpClient.get<FlightSearch>('/flights/search', { params })
  return data
}
