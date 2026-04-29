import { useEffect, useMemo, useState } from 'react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { MaskedDateInput, MaskedTimeInput } from '@/components/ui/masked-input'
import { Label } from '@/components/ui/label'

type Professional = {
  id: number
  name: string
  is_active: boolean
}

type Schedule = {
  id: number
  date: string
  time: string
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed'
  customer: { id: number; name: string }
  professional: { id: number; name: string } | null
}

type AvailableSlots = {
  date: string
  weekday: number
  available_slots: number
  total_available_minutes: number
  lunch_duration_minutes: number
  slot_duration_minutes: number
}

type Suggestion = {
  date: string
  time: string
  score: number
  source: string
}

const weekdays = [
  { value: 0, label: 'Segunda' },
  { value: 1, label: 'Terça' },
  { value: 2, label: 'Quarta' },
  { value: 3, label: 'Quinta' },
  { value: 4, label: 'Sexta' },
  { value: 5, label: 'Sábado' },
  { value: 6, label: 'Domingo' },
]

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [professionals, setProfessionals] = useState<Professional[]>([])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const [customerName, setCustomerName] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [professionalId, setProfessionalId] = useState('')

  const [availabilityDate, setAvailabilityDate] = useState('')
  const [slotInfo, setSlotInfo] = useState<AvailableSlots | null>(null)

  const [suggestCustomer, setSuggestCustomer] = useState('')
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])

  const activeProfessionals = useMemo(
    () => professionals.filter((professional) => professional.is_active),
    [professionals],
  )

  const load = async () => {
    const [scheduleRes, professionalsRes] = await Promise.all([
      api.get<Schedule[]>('/schedule/?skip=0&limit=100'),
      api.get<Professional[]>('/professionals/?skip=0&limit=100'),
    ])
    setSchedules(scheduleRes.data)
    setProfessionals(professionalsRes.data)
  }

  useEffect(() => {
    load().catch(() => setError('Não foi possível carregar dados de agendamento.'))
  }, [])

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (date.length !== 10 || time.length !== 5) {
      setError('Preencha a data e a hora completas antes de salvar.')
      return
    }

    setSaving(true)
    try {
      await api.post('/schedule/', {
        customer_name: customerName,
        date,
        time: `${time}:00`,
        professional_id: professionalId ? Number(professionalId) : null,
      })
      setCustomerName('')
      setDate('')
      setTime('')
      setProfessionalId('')
      await load()
    } catch {
      setError('Erro ao criar agendamento. Verifique data/hora e conflitos.')
    } finally {
      setSaving(false)
    }
  }

  const handleStatusChange = async (scheduleId: number, status: Schedule['status']) => {
    try {
      await api.patch(`/schedule/${scheduleId}/status`, { status })
      await load()
    } catch {
      setError('Não foi possível atualizar o status do agendamento.')
    }
  }

  const handleDeleteSchedule = async (scheduleId: number) => {
    const confirmed = window.confirm(
      'Deseja realmente excluir este agendamento? Esta ação não pode ser desfeita.',
    )
    if (!confirmed) return

    setError('')
    try {
      await api.delete(`/schedule/${scheduleId}`)
      await load()
    } catch {
      setError('Não foi possível excluir o agendamento.')
    }
  }

  const checkAvailability = async () => {
    setError('')

    if (availabilityDate.length !== 10) {
      setSlotInfo(null)
      setError('Informe uma data completa para consultar disponibilidade.')
      return
    }

    try {
      const { data } = await api.get<AvailableSlots>('/working-hours/slots', {
        params: { date: availabilityDate },
      })
      setSlotInfo(data)
    } catch {
      setSlotInfo(null)
      setError('Não foi possível consultar disponibilidade para este dia.')
    }
  }

  const getSuggestions = async () => {
    if (!suggestCustomer.trim()) return
    setError('')
    try {
      const { data } = await api.post<{ customer_name: string; suggestions: Suggestion[] }>(
        '/schedule/suggestions',
        {
          customer_name: suggestCustomer,
          limit: 5,
          search_days: 30,
        },
      )
      setSuggestions(data.suggestions)
    } catch {
      setSuggestions([])
      setError('Não foi possível buscar sugestões para este cliente.')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Criar agendamento</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-2 lg:grid-cols-5" onSubmit={handleCreateSchedule}>
            <div className="space-y-1">
              <Label htmlFor="customerName">Cliente</Label>
              <Input
                id="customerName"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="Nome do cliente"
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="date">Data (DD/MM/AAAA)</Label>
              <MaskedDateInput
                id="date"
                value={date}
                onValueChange={setDate}
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="time">Hora (HH:MM)</Label>
              <MaskedTimeInput
                id="time"
                value={time}
                onValueChange={setTime}
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="professional">Profissional (opcional)</Label>
              <select
                id="professional"
                className="w-full h-9 rounded-md border px-3 text-sm bg-white"
                value={professionalId}
                onChange={(e) => setProfessionalId(e.target.value)}
              >
                <option value="">Não definido</option>
                {activeProfessionals.map((professional) => (
                  <option key={professional.id} value={professional.id}>
                    {professional.name}
                  </option>
                ))}
              </select>
            </div>
            <Button className="self-end" type="submit" disabled={saving}>
              {saving ? 'Salvando...' : 'Criar'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Ver disponibilidade por dia</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-3">
              <MaskedDateInput value={availabilityDate} onValueChange={setAvailabilityDate} />
              <Button variant="outline" onClick={checkAvailability}>
                Consultar
              </Button>
            </div>
            {slotInfo && (
              <div className="rounded-md border p-3 text-sm text-slate-700 space-y-1">
                <p>Data: {slotInfo.date}</p>
                <p>Dia da semana: {weekdays.find((day) => day.value === slotInfo.weekday)?.label}</p>
                <p>Slots disponíveis: {slotInfo.available_slots}</p>
                <p>Minutos disponíveis: {slotInfo.total_available_minutes}</p>
                <p>Duração por slot: {slotInfo.slot_duration_minutes} min</p>
                <p>Intervalo de almoço: {slotInfo.lunch_duration_minutes} min</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sugestões automáticas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-3">
              <Input
                value={suggestCustomer}
                onChange={(e) => setSuggestCustomer(e.target.value)}
                placeholder="Nome do cliente"
              />
              <Button variant="outline" onClick={getSuggestions}>
                Sugerir
              </Button>
            </div>
            {!!suggestions.length && (
              <ul className="space-y-2 text-sm">
                {suggestions.map((suggestion, idx) => (
                  <li key={`${suggestion.date}-${suggestion.time}-${idx}`} className="rounded-md border p-2">
                    {suggestion.date} às {suggestion.time} · score {suggestion.score} · {suggestion.source}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Agendamentos</CardTitle>
        </CardHeader>
        <CardContent>
          {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2">Cliente</th>
                  <th className="py-2">Data</th>
                  <th className="py-2">Hora</th>
                  <th className="py-2">Profissional</th>
                  <th className="py-2">Status</th>
                  <th className="py-2">Ações</th>
                </tr>
              </thead>
              <tbody>
                {schedules.map((item) => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2">{item.customer?.name}</td>
                    <td className="py-2">{item.date}</td>
                    <td className="py-2">{item.time}</td>
                    <td className="py-2">{item.professional?.name ?? '-'}</td>
                    <td className="py-2">
                      <select
                        className="h-8 rounded-md border px-2 text-sm bg-white"
                        value={item.status}
                        onChange={(e) =>
                          handleStatusChange(item.id, e.target.value as Schedule['status'])
                        }
                      >
                        <option value="pending">pending</option>
                        <option value="confirmed">confirmed</option>
                        <option value="cancelled">cancelled</option>
                        <option value="completed">completed</option>
                      </select>
                    </td>
                    <td className="py-2">
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteSchedule(item.id)}
                      >
                        Excluir
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!schedules.length && <p className="text-slate-500 py-2">Sem agendamentos.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
