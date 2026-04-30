import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button, buttonVariants } from '@/components/ui/button'
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
  const [nextSchedules, setNextSchedules] = useState<Schedule[]>([])
  const [averageTicketAmount, setAverageTicketAmount] = useState(0)
  const [completedSchedules, setCompletedSchedules] = useState(0)
  const [totalRevenue, setTotalRevenue] = useState(0)
  const [revenueByProfessional, setRevenueByProfessional] = useState<RevenueByProfessionalItem[]>([])
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
    setNextSchedules(data.next_schedules)
  }

  const resetInsights = () => {
    setScheduleCount(0)
    setProfessionalCount(0)
    setCustomerCount(0)
    setAverageTicketAmount(0)
    setCompletedSchedules(0)
    setTotalRevenue(0)
    setRevenueByProfessional([])
    setNextSchedules([])
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
    api
      .get<DashboardInsights>('/dashboard/insights')
      .then(({ data }) => applyInsights(data))
      .catch(() => resetInsights())
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

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Filtro de período</CardTitle>
          <CardDescription>
            Filtra os insights de faturamento por intervalo de datas.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div className="space-y-1">
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
                className="w-full h-9 rounded-md border px-3 text-sm bg-white"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => openNativeDatePicker(startDateRef.current)}
              >
                Calendário
              </Button>
            </div>
          </div>
          <div className="space-y-1">
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
                className="w-full h-9 rounded-md border px-3 text-sm bg-white"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => openNativeDatePicker(endDateRef.current)}
              >
                Calendário
              </Button>
            </div>
          </div>
          <div className="md:col-span-2 flex items-end gap-2">
            <Button onClick={applyDateFilter}>Aplicar filtro</Button>
            <Button variant="outline" onClick={clearDateFilter}>
              Limpar
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total de agendamentos</CardDescription>
            <CardTitle className="text-3xl">{scheduleCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Profissionais</CardDescription>
            <CardTitle className="text-3xl">{professionalCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Clientes</CardDescription>
            <CardTitle className="text-3xl">{customerCount}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Próximos agendamentos</CardTitle>
            <CardDescription>Visão rápida dos registros mais recentes.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {nextSchedules.length ? (
              nextSchedules.map((schedule) => (
                <div key={schedule.id} className="rounded-md border p-3 text-sm">
                  <p className="font-medium">{schedule.customer?.name}</p>
                  <p className="text-slate-600">
                    {schedule.date} às {schedule.time} · {schedule.status}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">Sem agendamentos por enquanto.</p>
            )}
            <Link
              to="/schedules"
              className={cn(buttonVariants({ variant: 'outline' }), 'mt-2 inline-flex')}
            >
              Ir para Agendamentos
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Insights de faturamento</CardTitle>
            <CardDescription>
              Métricas calculadas no backend com base nas configurações da empresa.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-md border p-3">
              <p className="text-sm text-slate-600">Ticket médio configurado</p>
              <p className="text-xl font-semibold">{formatCurrency(averageTicketAmount)}</p>
            </div>

            <div className="rounded-md border p-3">
              <p className="text-sm text-slate-600">Faturamento total</p>
              <p className="text-2xl font-semibold">{formatCurrency(totalRevenue)}</p>
              <p className="text-xs text-slate-500">
                {completedSchedules} agendamento(s) concluído(s)
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Faturamento por profissional</p>
              {revenueByProfessional.length ? (
                revenueByProfessional.map((item) => (
                  <div key={`${item.professional_id ?? 'none'}-${item.professional_name}`} className="rounded-md border p-3 text-sm">
                    <p className="font-medium">{item.professional_name}</p>
                    <p className="text-slate-700">{formatCurrency(item.total_revenue)}</p>
                    <p className="text-xs text-slate-500">
                      {item.completed_schedules} atendimento(s) concluído(s)
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">Sem atendimentos concluídos para calcular.</p>
              )}
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
    </div>
  )
}
