import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button, buttonVariants } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/contexts/AuthContext'
import { cn } from '@/lib/utils'
import { api } from '@/services/api'

type CompanyLocalSettings = {
  companyDisplayName: string
  cancellationPolicy: string
  defaultTimezone: string
  reminderLeadMinutes: string
  averageTicketAmount: string
}

export default function CompanyAdminPage() {
  const { user } = useAuth()
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [settings, setSettings] = useState<CompanyLocalSettings>({
    companyDisplayName: '',
    cancellationPolicy: 'Cancelamentos sem aviso serão marcados internamente no histórico.',
    defaultTimezone: 'America/Sao_Paulo',
    reminderLeadMinutes: '120',
    averageTicketAmount: '100',
  })

  useEffect(() => {
    setLoading(true)
    api
      .get('/company-admin/')
      .then(({ data }) => {
        setSettings({
          companyDisplayName: data.display_name ?? '',
          cancellationPolicy:
            data.cancellation_policy ??
            'Cancelamentos sem aviso serão marcados internamente no histórico.',
          defaultTimezone: data.default_timezone ?? 'America/Sao_Paulo',
          reminderLeadMinutes: String(data.reminder_lead_minutes ?? 120),
          averageTicketAmount: String(data.average_ticket_amount ?? 100),
        })
      })
      .catch(() => setError('Não foi possível carregar configurações da empresa.'))
      .finally(() => setLoading(false))
  }, [])

  const save = async () => {
    setError('')
    setLoading(true)
    try {
      await api.put('/company-admin/', {
        display_name: settings.companyDisplayName || null,
        cancellation_policy: settings.cancellationPolicy || null,
        default_timezone: settings.defaultTimezone,
        reminder_lead_minutes: Number(settings.reminderLeadMinutes),
        average_ticket_amount: Number(settings.averageTicketAmount),
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch {
      setError('Não foi possível salvar configurações da empresa.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Administração da empresa</CardTitle>
          <CardDescription>
            Controles administrativos para operação diária do negócio.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1">
            <Label>ID da empresa</Label>
            <Input value={String(user?.company_id ?? '')} disabled />
          </div>
          <div className="space-y-1">
            <Label>Administrador logado</Label>
            <Input value={user?.name ?? ''} disabled />
          </div>
          <div className="space-y-1 md:col-span-2">
            <Label htmlFor="companyDisplayName">Nome de exibição da empresa</Label>
            <Input
              id="companyDisplayName"
              value={settings.companyDisplayName}
              onChange={(e) =>
                setSettings((prev) => ({ ...prev, companyDisplayName: e.target.value }))
              }
              placeholder="Ex.: Barbearia Prime"
            />
          </div>
          <div className="space-y-1 md:col-span-2">
            <Label htmlFor="cancellationPolicy">Política de cancelamento</Label>
            <textarea
              id="cancellationPolicy"
              className="w-full min-h-24 rounded-md border p-2 text-sm"
              value={settings.cancellationPolicy}
              onChange={(e) =>
                setSettings((prev) => ({ ...prev, cancellationPolicy: e.target.value }))
              }
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="defaultTimezone">Fuso horário padrão</Label>
            <Input
              id="defaultTimezone"
              value={settings.defaultTimezone}
              onChange={(e) => setSettings((prev) => ({ ...prev, defaultTimezone: e.target.value }))}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="reminderLeadMinutes">Antecedência lembrete (min)</Label>
            <Input
              id="reminderLeadMinutes"
              type="number"
              min="0"
              value={settings.reminderLeadMinutes}
              onChange={(e) =>
                setSettings((prev) => ({ ...prev, reminderLeadMinutes: e.target.value }))
              }
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="averageTicketAmount">Ticket médio padrão (R$)</Label>
            <Input
              id="averageTicketAmount"
              type="number"
              min="0"
              step="0.01"
              value={settings.averageTicketAmount}
              onChange={(e) =>
                setSettings((prev) => ({ ...prev, averageTicketAmount: e.target.value }))
              }
            />
          </div>
          <div className="md:col-span-2 flex items-center gap-3">
            <Button onClick={save} disabled={loading}>
              {loading ? 'Salvando...' : 'Salvar configurações'}
            </Button>
            {saved && <span className="text-sm text-green-600">Configurações salvas.</span>}
          </div>
          {error && <p className="md:col-span-2 text-sm text-red-600">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Atalhos administrativos</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Link to="/working-hours" className={cn(buttonVariants({ variant: 'outline' }), 'inline-flex')}>
            Horário de funcionamento e slots
          </Link>
          <Link to="/schedules" className={cn(buttonVariants({ variant: 'outline' }), 'inline-flex')}>
            Gestão de agendamentos
          </Link>
          <Link to="/agent" className={cn(buttonVariants({ variant: 'outline' }), 'inline-flex')}>
            Configuração do agente
          </Link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Persistência no banco</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-600">
          Esta tela agora salva e lê diretamente da API, persistindo as configurações administrativas no banco da empresa.
        </CardContent>
      </Card>
    </div>
  )
}
