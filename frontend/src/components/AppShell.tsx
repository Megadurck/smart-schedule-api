import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/AuthContext'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/company-admin', label: 'Admin Empresa' },
  { to: '/working-hours', label: 'Horários e Slots' },
  { to: '/professionals', label: 'Profissionais' },
  { to: '/customers', label: 'Clientes' },
  { to: '/schedules', label: 'Agendamentos' },
  { to: '/agent', label: 'Agente' },
]

export default function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold">Smart Schedule</h1>
            <p className="text-xs text-slate-500">
              Admin: {user?.name} · Empresa #{user?.company_id}
            </p>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            Sair
          </Button>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-6 grid gap-6 lg:grid-cols-[220px_1fr]">
        <aside className="bg-white rounded-lg border p-3 h-fit">
          <nav className="flex flex-col gap-2">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-md px-3 py-2 text-sm ${
                    isActive
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
