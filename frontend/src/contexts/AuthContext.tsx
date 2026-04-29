import { createContext, useContext, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import { api } from '@/services/api'

interface AuthUser {
  id: number
  name: string
  company_id: number
}

interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (company_name: string, user_name: string, password: string) => Promise<void>
  register: (company_name: string, user_name: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const stored = localStorage.getItem('user')
    return stored ? (JSON.parse(stored) as AuthUser) : null
  })

  const saveTokens = (access_token: string, refresh_token: string) => {
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
  }

  const fetchMe = useCallback(async (): Promise<AuthUser> => {
    const { data } = await api.get<AuthUser>('/auth/me')
    localStorage.setItem('user', JSON.stringify(data))
    setUser(data)
    return data
  }, [])

  const login = async (company_name: string, user_name: string, password: string) => {
    const { data } = await api.post('/auth/login', { company_name, user_name, password })
    saveTokens(data.access_token, data.refresh_token)
    await fetchMe()
  }

  const register = async (company_name: string, user_name: string, password: string) => {
    const { data } = await api.post('/auth/register', { company_name, user_name, password })
    saveTokens(data.access_token, data.refresh_token)
    await fetchMe()
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
