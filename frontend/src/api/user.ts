import { httpClient } from './http'

export type UserProfile = {
  id: number
  name: string
  surname: string
  profile_photo: string | null
  username: string
  email: string
  default_currency: string
}

export type UserProfilePayload = Omit<UserProfile, 'id'>

export async function getCurrentUser(): Promise<UserProfile> {
  const { data } = await httpClient.get<UserProfile>('/users/me')
  return data
}

export async function updateCurrentUser(
  payload: UserProfilePayload,
): Promise<UserProfile> {
  const { data } = await httpClient.patch<UserProfile>('/users/me', payload)
  return data
}

export async function deleteCurrentUser(): Promise<void> {
  await httpClient.delete('/users/me')
}

export async function getCurrentUserPhoto(): Promise<string> {
  const { data } = await httpClient.get<Blob>('/users/me/profile-photo', {
    responseType: 'blob',
  })
  return await new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(data)
  })
}

export async function uploadCurrentUserPhoto(file: File): Promise<UserProfile> {
  const formData = new FormData()
  formData.append('photo', file)
  const { data } = await httpClient.post<UserProfile>('/users/me/profile-photo', formData, {
    // El cliente general usa JSON. Al anularlo, el navegador añade el
    // boundary multipart correcto para FormData.
    headers: { 'Content-Type': null },
  })
  return data
}

export async function deleteCurrentUserPhoto(): Promise<void> {
  await httpClient.delete('/users/me/profile-photo')
}
