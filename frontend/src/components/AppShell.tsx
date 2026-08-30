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
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(99,102,241,0.16),transparent_28%),linear-gradient(180deg,#f4f7fb_0%,#eef2ff_100%)] dark:bg-[radial-gradient(circle_at_top,rgba(99,102,241,0.18),transparent_24%),linear-gradient(180deg,#020817_0%,#0f172a_100%)]">
      <header className="sticky top-0 z-20 border-b border-border/60 bg-background/75 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 pr-24 sm:px-6 sm:pr-28">
          <div>
            <div className="mb-1 flex items-center gap-2">
              <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500 shadow-[0_0_18px_rgba(16,185,129,0.9)]" />
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
        <aside className="h-fit rounded-2xl border border-border/70 bg-card/80 p-3 shadow-[0_20px_45px_rgba(15,23,42,0.08)] backdrop-blur-sm dark:shadow-[0_20px_45px_rgba(2,6,23,0.38)]">
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
                      ? 'bg-linear-to-r from-slate-900 to-indigo-700 text-white shadow-lg shadow-indigo-500/20 dark:from-indigo-500 dark:to-violet-500'
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
          <div className="rounded-2xl border border-border/60 bg-card/70 p-4 shadow-[0_20px_45px_rgba(15,23,42,0.05)] backdrop-blur-sm dark:shadow-[0_20px_45px_rgba(2,6,23,0.3)] sm:p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
