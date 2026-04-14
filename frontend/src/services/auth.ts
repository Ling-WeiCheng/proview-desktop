import api from './api'

export interface AuthUser {
  id: number
  username: string
  display_name: string
  created_at: string
}

export async function fetchMe(): Promise<AuthUser> {
  const { data } = await api.get('/api/auth/me')
  return data.user
}
