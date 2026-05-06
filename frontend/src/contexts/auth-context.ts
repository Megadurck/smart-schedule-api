import { createContext } from 'react'

export interface AuthUser {
  id: number
  name: string
  company_id: number
}

export interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (company_name: string, user_name: string, password: string) => Promise<void>
  register: (company_name: string, user_name: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextType | null>(null)