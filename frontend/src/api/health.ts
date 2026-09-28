import { httpClient } from './http'

export interface HealthResponse {
  status: string
  database: string
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await httpClient.get<HealthResponse>('/health')

  return response.data
}