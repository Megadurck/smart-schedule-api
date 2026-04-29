import { useEffect, useState } from 'react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type Professional = {
  id: number
  name: string
  is_active: boolean
}

export default function ProfessionalsPage() {
  const [items, setItems] = useState<Professional[]>([])
  const [name, setName] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    const { data } = await api.get<Professional[]>('/professionals/')
    setItems(data)
  }

  useEffect(() => {
    load().catch(() => setError('Não foi possível carregar profissionais.'))
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/professionals/', { name, is_active: isActive })
      setName('')
      setIsActive(true)
      await load()
    } catch {
      setError('Erro ao cadastrar profissional.')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (professionalId: number) => {
    const confirmed = window.confirm('Deseja realmente excluir este profissional?')
    if (!confirmed) return

    setError('')
    try {
      await api.delete(`/professionals/${professionalId}`)
      await load()
    } catch {
      setError('Não foi possível excluir profissional.')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Cadastro de profissional</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-[1fr_auto_auto]" onSubmit={handleCreate}>
            <div className="space-y-1">
              <Label htmlFor="name">Nome</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Nome do profissional"
                required
              />
            </div>
            <label className="flex items-center gap-2 text-sm mt-6">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
              />
              Ativo
            </label>
            <Button className="mt-6" type="submit" disabled={loading}>
              {loading ? 'Salvando...' : 'Cadastrar'}
            </Button>
          </form>
          {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Profissionais da empresa</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2">ID</th>
                  <th className="py-2">Nome</th>
                  <th className="py-2">Status</th>
                  <th className="py-2">Ações</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2">{item.id}</td>
                    <td className="py-2">{item.name}</td>
                    <td className="py-2">{item.is_active ? 'Ativo' : 'Inativo'}</td>
                    <td className="py-2">
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(item.id)}
                      >
                        Excluir
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!items.length && <p className="text-slate-500 py-2">Sem profissionais cadastrados.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
