import { useEffect, useState } from 'react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type WorkingHours = {
  id: number
  weekday: number
  start_time: string
  end_time: string
  slot_duration_minutes: number
  lunch_start: string | null
  lunch_end: string | null
  is_active: boolean
}

type AvailableSlots = {
  weekday: number
  available_slots: number
  total_available_minutes: number
  lunch_duration_minutes: number
  slot_duration_minutes: number
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

export default function WorkingHoursPage() {
  const [items, setItems] = useState<WorkingHours[]>([])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [slotInfo, setSlotInfo] = useState<AvailableSlots | null>(null)

  const [weekday, setWeekday] = useState('0')
  const [startTime, setStartTime] = useState('08:00:00')
  const [endTime, setEndTime] = useState('18:00:00')
  const [slotDuration, setSlotDuration] = useState('30')
  const [lunchStart, setLunchStart] = useState('12:00:00')
  const [lunchEnd, setLunchEnd] = useState('13:00:00')

  const load = async () => {
    const { data } = await api.get<WorkingHours[]>('/working-hours/')
    setItems(data)
  }

  useEffect(() => {
    load().catch(() => setError('Não foi possível carregar horários de funcionamento.'))
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await api.post('/working-hours/', {
        weekday: Number(weekday),
        start_time: startTime,
        end_time: endTime,
        slot_duration_minutes: Number(slotDuration),
        lunch_start: lunchStart || null,
        lunch_end: lunchEnd || null,
      })
      await load()
    } catch {
      setError('Erro ao salvar horário. Verifique os campos e a regra de almoço.')
    } finally {
      setSaving(false)
    }
  }

  const checkSlots = async () => {
    setError('')
    try {
      const { data } = await api.get<AvailableSlots>(`/working-hours/slots/${weekday}`)
      setSlotInfo(data)
    } catch {
      setSlotInfo(null)
      setError('Não foi possível consultar slots disponíveis para o dia selecionado.')
    }
  }

  const weekdayLabel = (value: number) => {
    return weekdays.find((day) => day.value === value)?.label ?? `Dia ${value}`
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Horário de funcionamento e slots</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-3 lg:grid-cols-4" onSubmit={handleSave}>
            <div className="space-y-1">
              <Label htmlFor="weekday">Dia da semana</Label>
              <select
                id="weekday"
                className="w-full h-9 rounded-md border px-3 text-sm bg-white"
                value={weekday}
                onChange={(e) => setWeekday(e.target.value)}
              >
                {weekdays.map((day) => (
                  <option key={day.value} value={day.value}>
                    {day.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="startTime">Início</Label>
              <Input id="startTime" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            </div>

            <div className="space-y-1">
              <Label htmlFor="endTime">Fim</Label>
              <Input id="endTime" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            </div>

            <div className="space-y-1">
              <Label htmlFor="slotDuration">Duração do slot (min)</Label>
              <Input
                id="slotDuration"
                type="number"
                min="5"
                value={slotDuration}
                onChange={(e) => setSlotDuration(e.target.value)}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="lunchStart">Início almoço</Label>
              <Input
                id="lunchStart"
                value={lunchStart}
                onChange={(e) => setLunchStart(e.target.value)}
                placeholder="12:00:00"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="lunchEnd">Fim almoço</Label>
              <Input
                id="lunchEnd"
                value={lunchEnd}
                onChange={(e) => setLunchEnd(e.target.value)}
                placeholder="13:00:00"
              />
            </div>

            <div className="flex items-end gap-2">
              <Button type="submit" disabled={saving}>
                {saving ? 'Salvando...' : 'Salvar dia'}
              </Button>
              <Button type="button" variant="outline" onClick={checkSlots}>
                Ver slots
              </Button>
            </div>
          </form>
          {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
        </CardContent>
      </Card>

      {slotInfo && (
        <Card>
          <CardHeader>
            <CardTitle>Disponibilidade do dia</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-700 space-y-1">
            <p>Dia: {weekdayLabel(slotInfo.weekday)}</p>
            <p>Slots disponíveis: {slotInfo.available_slots}</p>
            <p>Minutos disponíveis: {slotInfo.total_available_minutes}</p>
            <p>Duração por slot: {slotInfo.slot_duration_minutes} min</p>
            <p>Intervalo de almoço: {slotInfo.lunch_duration_minutes} min</p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Horários configurados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2">Dia</th>
                  <th className="py-2">Expediente</th>
                  <th className="py-2">Slot</th>
                  <th className="py-2">Almoço</th>
                  <th className="py-2">Ativo</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2">{weekdayLabel(item.weekday)}</td>
                    <td className="py-2">{item.start_time} - {item.end_time}</td>
                    <td className="py-2">{item.slot_duration_minutes} min</td>
                    <td className="py-2">{item.lunch_start ?? '-'} - {item.lunch_end ?? '-'}</td>
                    <td className="py-2">{item.is_active ? 'Sim' : 'Não'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!items.length && <p className="text-slate-500 py-2">Nenhum horário configurado.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
