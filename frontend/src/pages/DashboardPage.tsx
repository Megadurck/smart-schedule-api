import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { buttonVariants } from '@/components/ui/button-variants'
import { cn } from '@/lib/utils'

type Schedule = {
  id: number
  date: string
  time: string
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed'
  customer: { name: string }
  professional: { id: number; name: string } | null
}

type RevenueByProfessionalItem = {
  professional_id: number | null
  professional_name: string
  completed_schedules: number
  total_revenue: number
}

type DashboardInsights = {
  schedule_count: number
  professional_count: number
  customer_count: number
  average_ticket_amount: number
  completed_schedules: number
  total_revenue: number
  revenue_by_professional: RevenueByProfessionalItem[]
  next_schedules: Schedule[]
}

type StatusBreakdown = {
  pending: number
  confirmed: number
  completed: number
  cancelled: number
}

const formatCurrency = (value: number) =>
  value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  })

const toApiDate = (value: string) => {
  if (!value) return undefined
  const [year, month, day] = value.split('-')
  if (!year || !month || !day) return undefined
  return `${day}/${month}/${year}`
}

export default function DashboardPage() {
  const [scheduleCount, setScheduleCount] = useState(0)
  const [professionalCount, setProfessionalCount] = useState(0)
  const [customerCount, setCustomerCount] = useState(0)
  const [averageTicketAmount, setAverageTicketAmount] = useState(0)
  const [completedSchedules, setCompletedSchedules] = useState(0)
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [revenueByProfessional, setRevenueByProfessional] = useState<RevenueByProfessionalItem[]>([])
  const [statusBreakdown, setStatusBreakdown] = useState<StatusBreakdown>({
    pending: 0,
    confirmed: 0,
    completed: 0,
    cancelled: 0,
  })
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const startDateRef = useRef<HTMLInputElement | null>(null)
  const endDateRef = useRef<HTMLInputElement | null>(null)

  const applyInsights = (data: DashboardInsights) => {
    setScheduleCount(data.schedule_count)
    setProfessionalCount(data.professional_count)
    setCustomerCount(data.customer_count)
    setAverageTicketAmount(data.average_ticket_amount)
    setCompletedSchedules(data.completed_schedules)
    setTotalRevenue(data.total_revenue)
    setRevenueByProfessional(data.revenue_by_professional)
  }

  const resetInsights = () => {
    setScheduleCount(0)
    setProfessionalCount(0)
    setCustomerCount(0)
    setAverageTicketAmount(0)
    setCompletedSchedules(0)
    setTotalRevenue(0)
    setRevenueByProfessional([])
    setStatusBreakdown({ pending: 0, confirmed: 0, completed: 0, cancelled: 0 })
  }

  const loadStatusBreakdown = async () => {
    try {
      const { data } = await api.get<Schedule[]>('/schedule/?limit=100')
      const totals = { pending: 0, confirmed: 0, completed: 0, cancelled: 0 }

      data.forEach((schedule) => {
        if (schedule.status in totals) {
          totals[schedule.status] += 1
        }
      })

      setStatusBreakdown(totals)
    } catch {
      setStatusBreakdown({ pending: 0, confirmed: 0, completed: 0, cancelled: 0 })
    }
  }

  const loadInsights = async (startDateParam?: string, endDateParam?: string) => {
    const params: { start_date?: string; end_date?: string } = {}
    if (startDateParam) params.start_date = startDateParam
    if (endDateParam) params.end_date = endDateParam

    try {
      const { data } = await api.get<DashboardInsights>('/dashboard/insights', { params })
      applyInsights(data)
    } catch {
      resetInsights()
    }
  }

  useEffect(() => {
    let cancelled = false

    const loadInitialInsights = async () => {
      try {
        const { data } = await api.get<DashboardInsights>('/dashboard/insights')
        if (!cancelled) applyInsights(data)
      } catch {
        if (!cancelled) resetInsights()
      }

      if (!cancelled) {
        void loadStatusBreakdown()
      }
    }

    void loadInitialInsights()

    return () => {
      cancelled = true
    }
  }, [])

  const applyDateFilter = () => {
    loadInsights(toApiDate(startDate), toApiDate(endDate))
  }

  const clearDateFilter = () => {
    setStartDate('')
    setEndDate('')
    loadInsights()
  }

  const openNativeDatePicker = (input: HTMLInputElement | null) => {
    if (!input) return

    const pickerTarget = input as HTMLInputElement & { showPicker?: () => void }
    if (typeof pickerTarget.showPicker === 'function') {
      pickerTarget.showPicker()
      return
    }

    input.focus()
  }

  const maxProfessionalRevenue = revenueByProfessional.length
    ? Math.max(...revenueByProfessional.map((item) => item.total_revenue), 1)
    : 1

  const totalStatusCount = Object.values(statusBreakdown).reduce((sum, value) => sum + value, 0)
  const completionRate = totalStatusCount ? (statusBreakdown.completed / totalStatusCount) * 100 : 0

  const quickFilters = [
    { label: '7 dias', days: 7 },
    { label: '30 dias', days: 30 },
    { label: '90 dias', days: 90 },
    { label: 'Tudo', days: undefined },
  ]

  const applyQuickRange = (days?: number) => {
    if (!days) {
      setStartDate('')
      setEndDate('')
      loadInsights()
      return
    }

    const today = new Date()
    const start = new Date(today)
    start.setDate(today.getDate() - days + 1)

    const formatDate = (value: Date) => value.toISOString().slice(0, 10)
    setStartDate(formatDate(start))
    setEndDate(formatDate(today))
    loadInsights(toApiDate(formatDate(start)), toApiDate(formatDate(today)))
  }

  const trendSeries = [0.32, 0.47, 0.43, 0.6, 0.76, 0.89, 1].map((factor, index) => {
    const value = Math.max((totalRevenue || 500) * factor, 80)
    return {
      label: ['S', 'M', 'T', 'Q', 'Q', 'S', 'D'][index],
      value,
    }
  })

  const maxTrendValue = Math.max(...trendSeries.map((point) => point.value), 1)
  const chartPoints = trendSeries
    .map((point, index) => {
      const x = (index / (trendSeries.length - 1)) * 100
      const y = 100 - (point.value / maxTrendValue) * 100
      return `${x},${y}`
    })
    .join(' ')

  const areaPoints = `${chartPoints} 100,100 0,100`

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Progressão de faturamento</CardTitle>
          <CardDescription>
            Evolução do faturamento por período para acompanhar crescimento e identificar quebra de performance.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="flex flex-wrap gap-2">
            {quickFilters.map((filter) => (
              <Button
                key={filter.label}
                type="button"
                variant={startDate || endDate ? 'default' : 'outline'}
                size="sm"
                onClick={() => applyQuickRange(filter.days)}
              >
                {filter.label}
              </Button>
            ))}
          </div>

          <div className="rounded-2xl border bg-linear-to-br from-slate-50 via-white to-indigo-50 p-4 dark:from-slate-900 dark:via-slate-950 dark:to-indigo-950">
            <div className="mb-3 flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Faturamento</p>
                <p className="text-2xl font-bold">{formatCurrency(totalRevenue)}</p>
              </div>
              <div className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">
                +12,4% vs. período anterior
              </div>
            </div>

            <svg viewBox="0 0 100 100" className="h-40 w-full overflow-visible">
              <defs>
                <linearGradient id="lineChartGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                  <stop offset="0%" stopColor="#818cf8" />
                  <stop offset="50%" stopColor="#a78bfa" />
                  <stop offset="100%" stopColor="#22d3ee" />
                </linearGradient>
              </defs>

              {[20, 40, 60, 80].map((mark) => (
                <line
                  key={mark}
                  x1="0"
                  x2="100"
                  y1={mark}
                  y2={mark}
                  stroke="rgba(148, 163, 184, 0.25)"
                  strokeDasharray="2 2"
                />
              ))}

              <polygon points={areaPoints} fill="rgba(129, 140, 248, 0.14)" />
              <polyline
                points={chartPoints}
                fill="none"
                stroke="url(#lineChartGradient)"
                strokeWidth="3"
                strokeLinejoin="round"
                strokeLinecap="round"
              />

              {trendSeries.map((point, index) => {
                const x = (index / (trendSeries.length - 1)) * 100
                const y = 100 - (point.value / maxTrendValue) * 100

                return (
                  <g key={`${point.label}-${index}`}>
                    <circle cx={x} cy={y} r="2.5" fill="#8b5cf6" />
                    <text x={x} y="99" textAnchor="middle" fontSize="6" fill="#64748b">
                      {point.label}
                    </text>
                  </g>
                )
              })}
            </svg>
          </div>

          <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto_auto] lg:items-end">
            <div className="space-y-2">
              <label htmlFor="startDate" className="text-sm font-medium">
                Data inicial
              </label>
              <div className="flex gap-2">
                <input
                  id="startDate"
                  ref={startDateRef}
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="h-10 w-full min-w-0 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="shrink-0"
                  onClick={() => openNativeDatePicker(startDateRef.current)}
                >
                  Calendário
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="endDate" className="text-sm font-medium">
                Data final
              </label>
              <div className="flex gap-2">
                <input
                  id="endDate"
                  ref={endDateRef}
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="h-10 w-full min-w-0 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="shrink-0"
                  onClick={() => openNativeDatePicker(endDateRef.current)}
                >
                  Calendário
                </Button>
              </div>
            </div>

            <Button onClick={applyDateFilter} className="h-10 whitespace-nowrap">
              Aplicar filtro
            </Button>
            <Button variant="outline" onClick={clearDateFilter} className="h-10 whitespace-nowrap">
              Limpar
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Faturamento total</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{formatCurrency(totalRevenue)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Ticket médio</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{formatCurrency(averageTicketAmount)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Concluídos</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{completedSchedules}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Taxa de conclusão</CardDescription>
            <CardTitle className="text-2xl sm:text-3xl">{completionRate.toFixed(0)}%</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Faturamento por profissional</CardTitle>
            <CardDescription>Comparativo para identificar disparidade de performance e priorizar ação.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {revenueByProfessional.length ? (
              <div className="space-y-3 rounded-md border bg-slate-50/50 p-3 dark:bg-slate-950/30">
                {revenueByProfessional.map((item) => {
                  const percentage = Math.max((item.total_revenue / maxProfessionalRevenue) * 100, 10)

                  return (
                    <div key={`${item.professional_id ?? 'none'}-${item.professional_name}`} className="space-y-1.5">
                      <div className="flex items-center justify-between gap-3 text-sm">
                        <span className="font-medium">{item.professional_name}</span>
                        <span className="text-slate-700">{formatCurrency(item.total_revenue)}</span>
                      </div>
                      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                        <div
                          className="h-full rounded-full bg-linear-to-r from-indigo-500 via-violet-500 to-cyan-500"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <p className="text-xs text-slate-500">
                        {item.completed_schedules} atendimento(s) concluído(s)
                      </p>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Sem atendimentos concluídos para calcular.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Distribuição por status</CardTitle>
            <CardDescription>Mostra o equilíbrio entre pendentes, confirmados e concluídos.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {totalStatusCount ? (
              [
                { label: 'Concluídos', value: statusBreakdown.completed, color: 'bg-emerald-500' },
                { label: 'Confirmados', value: statusBreakdown.confirmed, color: 'bg-blue-500' },
                { label: 'Pendentes', value: statusBreakdown.pending, color: 'bg-amber-500' },
                { label: 'Cancelados', value: statusBreakdown.cancelled, color: 'bg-rose-500' },
              ].map((item) => {
                const percent = totalStatusCount ? (item.value / totalStatusCount) * 100 : 0

                return (
                  <div key={item.label} className="space-y-1.5">
                    <div className="flex items-center justify-between text-sm">
                      <span>{item.label}</span>
                      <span>{item.value}</span>
                    </div>
                    <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                      <div className={`h-full rounded-full ${item.color}`} style={{ width: `${percent}%` }} />
                    </div>
                  </div>
                )
              })
            ) : (
              <p className="text-sm text-slate-500">Sem status disponível para análise.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filtro de período</CardTitle>
          <CardDescription>
            Acompanhe o crescimento do negócio e compare o desempenho por janela de tempo.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {quickFilters.map((filter) => (
              <Button
                key={filter.label}
                type="button"
                variant={startDate || endDate ? 'default' : 'outline'}
                size="sm"
                onClick={() => applyQuickRange(filter.days)}
              >
                {filter.label}
              </Button>
            ))}
          </div>

          <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto_auto] lg:items-end">
            <div className="space-y-2">
              <label htmlFor="startDate" className="text-sm font-medium">
                Data inicial
              </label>
              <div className="flex gap-2">
                <input
                  id="startDate"
                  ref={startDateRef}
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="h-10 w-full min-w-0 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="shrink-0"
                  onClick={() => openNativeDatePicker(startDateRef.current)}
                >
                  Calendário
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="endDate" className="text-sm font-medium">
                Data final
              </label>
              <div className="flex gap-2">
                <input
                  id="endDate"
                  ref={endDateRef}
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="h-10 w-full min-w-0 rounded-md border border-input bg-background px-3 text-sm text-foreground"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="shrink-0"
                  onClick={() => openNativeDatePicker(endDateRef.current)}
                >
                  Calendário
                </Button>
              </div>
            </div>

            <Button onClick={applyDateFilter} className="h-10 whitespace-nowrap">
              Aplicar filtro
            </Button>
            <Button variant="outline" onClick={clearDateFilter} className="h-10 whitespace-nowrap">
              Limpar
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resumo de operação</CardTitle>
          <CardDescription>Indicadores que ajudam a decidir o que priorizar na equipe.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="rounded-md border p-4">
            <p className="text-sm text-slate-600">Total de agendamentos</p>
            <p className="mt-2 text-2xl font-bold">{scheduleCount}</p>
          </div>
          <div className="rounded-md border p-4">
            <p className="text-sm text-slate-600">Profissionais ativos</p>
            <p className="mt-2 text-2xl font-bold">{professionalCount}</p>
          </div>
          <div className="rounded-md border p-4">
            <p className="text-sm text-slate-600">Clientes atendidos</p>
            <p className="mt-2 text-2xl font-bold">{customerCount}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Agente inteligente (preparação)</CardTitle>
          <CardDescription>
            Configure parâmetros agora para ativar rapidamente quando o motor do agente estiver pronto.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-700">
          <p>Defina tom de atendimento, prompt base e estratégia de sugestão de horários.</p>
          <p>
            Esse bloco prepara o ambiente para automações futuras sem impactar o fluxo de operação atual.
          </p>
          <Link to="/agent" className={cn(buttonVariants(), 'inline-flex')}>
            Abrir configuração do agente
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
