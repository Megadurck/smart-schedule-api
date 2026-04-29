import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type Schedule = { id: number; date: string; time: string; status: string; customer: { name: string } }
type Professional = { id: number }
type Customer = { id: number }

export default function DashboardPage() {
  const [scheduleCount, setScheduleCount] = useState(0)
  const [professionalCount, setProfessionalCount] = useState(0)
  const [customerCount, setCustomerCount] = useState(0)
  const [nextSchedules, setNextSchedules] = useState<Schedule[]>([])

  useEffect(() => {
    Promise.all([
      api.get<Schedule[]>('/schedule/?skip=0&limit=100'),
      api.get<Professional[]>('/professionals/?skip=0&limit=100'),
      api.get<Customer[]>('/customers/?skip=0&limit=100'),
    ])
      .then(([schedulesRes, professionalsRes, customersRes]) => {
        setScheduleCount(schedulesRes.data.length)
        setProfessionalCount(professionalsRes.data.length)
        setCustomerCount(customersRes.data.length)
        setNextSchedules(schedulesRes.data.slice(0, 5))
      })
      .catch(() => {
        setScheduleCount(0)
        setProfessionalCount(0)
        setCustomerCount(0)
      })
  }, [])

  return (
    <div className="space-y-6">
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
