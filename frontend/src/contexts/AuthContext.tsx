import { createContext, useContext, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import { api } from '@/services/api'

const AUTH_USER_KEY = 'user'
const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

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
    const stored = sessionStorage.getItem(AUTH_USER_KEY)
    return stored ? (JSON.parse(stored) as AuthUser) : null
  })

  const saveTokens = (access_token: string, refresh_token: string) => {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, access_token)
    sessionStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
  }

  const fetchMe = useCallback(async (): Promise<AuthUser> => {
    const { data } = await api.get<AuthUser>('/auth/me')
    sessionStorage.setItem(AUTH_USER_KEY, JSON.stringify(data))
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
    sessionStorage.removeItem(AUTH_USER_KEY)
    sessionStorage.removeItem(ACCESS_TOKEN_KEY)
    sessionStorage.removeItem(REFRESH_TOKEN_KEY)
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
