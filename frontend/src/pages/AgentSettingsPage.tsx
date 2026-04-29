import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type AgentSettings = {
  enabled: boolean
  model: string
  tone: string
  systemPrompt: string
}

const STORAGE_KEY = 'smart_schedule_agent_settings'

export default function AgentSettingsPage() {
  const [settings, setSettings] = useState<AgentSettings>({
    enabled: false,
    model: 'gpt-5.3-codex',
    tone: 'profissional',
    systemPrompt: 'Você é um assistente para apoiar o atendimento e organização da agenda.',
  })
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      setSettings(JSON.parse(raw) as AgentSettings)
    }
  }, [])

  const save = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Configuração do Agente</CardTitle>
          <CardDescription>
            Terreno preparado para quando o agente inteligente for habilitado no backend.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={settings.enabled}
              onChange={(e) => setSettings((prev) => ({ ...prev, enabled: e.target.checked }))}
            />
            Ativar agente para sugestões automáticas
          </label>

          <div className="space-y-1">
            <Label htmlFor="model">Modelo</Label>
            <Input
              id="model"
              value={settings.model}
              onChange={(e) => setSettings((prev) => ({ ...prev, model: e.target.value }))}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="tone">Tom de resposta</Label>
            <Input
              id="tone"
              value={settings.tone}
              onChange={(e) => setSettings((prev) => ({ ...prev, tone: e.target.value }))}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="prompt">Prompt base</Label>
            <textarea
              id="prompt"
              className="w-full min-h-28 rounded-md border p-2 text-sm"
              value={settings.systemPrompt}
              onChange={(e) =>
                setSettings((prev) => ({ ...prev, systemPrompt: e.target.value }))
              }
            />
          </div>

          <div className="flex items-center gap-3">
            <Button onClick={save}>Salvar configuração</Button>
            {saved && <span className="text-sm text-green-600">Configuração salva.</span>}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
