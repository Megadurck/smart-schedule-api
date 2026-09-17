import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/useAuth'
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
    <div className="min-h-screen bg-[radial-gradient(58%_32%_at_50%_-6%,rgba(179,124,62,0.2),transparent_68%),linear-gradient(180deg,#f7f1e6_0%,#eee5d7_100%)] dark:bg-[radial-gradient(56%_30%_at_50%_-4%,rgba(179,124,62,0.24),transparent_70%),linear-gradient(180deg,#090b10_0%,#11141b_55%,#151922_100%)]">
      <header className="sticky top-0 z-20 border-b border-border/60 bg-background/75 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 pr-24 sm:px-6 sm:pr-28">
          <div>
            <div className="mb-1 flex items-center gap-2">
              <span className="inline-flex h-2.5 w-2.5 rounded-full bg-amber-500 shadow-[0_0_16px_rgba(245,158,11,0.8)]" />
              <h1 className="text-lg font-semibold tracking-tight text-foreground">Smart Schedule</h1>
            </div>
            <p className="text-xs text-muted-foreground">
              Admin: {user?.name} · Empresa #{user?.company_id}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={handleLogout} className="rounded-full px-4 shadow-sm">
              Sair
            </Button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[240px_1fr]">
        <aside className="h-fit rounded-2xl border border-border/70 bg-card/82 p-3 shadow-[0_20px_45px_rgba(25,18,8,0.14)] backdrop-blur-sm dark:shadow-[0_20px_45px_rgba(4,6,12,0.52)]">
          <div className="mb-3 px-3 pt-1">
            <p className="text-[10px] font-medium uppercase tracking-[0.22em] text-muted-foreground">
              Menu
            </p>
          </div>
          <nav className="flex flex-col gap-2">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-linear-to-r from-zinc-900 via-zinc-800 to-amber-800 text-amber-50 shadow-lg shadow-amber-700/20 dark:from-zinc-700 dark:via-zinc-700 dark:to-amber-600'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0">
          <div className="rounded-2xl border border-border/60 bg-card/78 p-4 shadow-[0_20px_45px_rgba(20,14,8,0.1)] backdrop-blur-sm dark:shadow-[0_20px_45px_rgba(4,6,12,0.42)] sm:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
