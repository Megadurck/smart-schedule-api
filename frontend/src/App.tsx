import { useEffect, useState, type ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MoonStar, SunMedium } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { AuthProvider } from '@/contexts/AuthContext'
import { useAuth } from '@/contexts/useAuth'
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
import LandingPage from '@/pages/LandingPage'

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
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />
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

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function ThemeToggle() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('smart-schedule-theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    document.documentElement.style.colorScheme = darkMode ? 'dark' : 'light'
    localStorage.setItem('smart-schedule-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      className="fixed right-4 top-4 z-50 h-11 w-11 rounded-full border-white/20 bg-background/80 shadow-lg backdrop-blur-sm sm:right-6 dark:bg-slate-900/80"
      onClick={() => setDarkMode((current) => !current)}
      aria-label="Alternar tema"
    >
      {darkMode ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
    </Button>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      <ThemeToggle />
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </div>
  )
}
