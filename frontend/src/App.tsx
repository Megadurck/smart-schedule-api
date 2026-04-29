import type { ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import AppShell from '@/components/AppShell'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import ProfessionalsPage from '@/pages/ProfessionalsPage'
import CustomersPage from '@/pages/CustomersPage'
import SchedulesPage from '@/pages/SchedulesPage'
import AgentSettingsPage from '@/pages/AgentSettingsPage'
import WorkingHoursPage from '@/pages/WorkingHoursPage'
import CompanyAdminPage from '@/pages/CompanyAdminPage'

function PrivateRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />

      <Route
        element={
          <PrivateRoute>
            <AppShell />
          </PrivateRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/company-admin" element={<CompanyAdminPage />} />
        <Route path="/working-hours" element={<WorkingHoursPage />} />
        <Route path="/professionals" element={<ProfessionalsPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/schedules" element={<SchedulesPage />} />
        <Route path="/agent" element={<AgentSettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
