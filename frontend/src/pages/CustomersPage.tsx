import { useEffect, useState } from 'react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type Customer = {
  id: number
  name: string
}

export default function CustomersPage() {
  const [items, setItems] = useState<Customer[]>([])
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    const { data } = await api.get<Customer[]>('/customers/')
    setItems(data)
  }

  useEffect(() => {
    load().catch(() => setError('Não foi possível carregar clientes.'))
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/customers/', { name })
      setName('')
      await load()
    } catch {
      setError('Erro ao cadastrar cliente.')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (customerId: number) => {
    const confirmed = window.confirm('Deseja realmente excluir este cliente?')
    if (!confirmed) return

    setError('')
    try {
      await api.delete(`/customers/${customerId}`)
      await load()
    } catch {
      setError('Não foi possível excluir cliente.')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Cadastro de cliente</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-[1fr_auto]" onSubmit={handleCreate}>
            <div className="space-y-1">
              <Label htmlFor="name">Nome</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Nome do cliente"
                required
              />
            </div>
            <Button className="mt-6" type="submit" disabled={loading}>
              {loading ? 'Salvando...' : 'Cadastrar'}
            </Button>
          </form>
          {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Clientes da empresa</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2">ID</th>
                  <th className="py-2">Nome</th>
                  <th className="py-2">Ações</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2">{item.id}</td>
                    <td className="py-2">{item.name}</td>
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
            {!items.length && <p className="text-slate-500 py-2">Sem clientes cadastrados.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
