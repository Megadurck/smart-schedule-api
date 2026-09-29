import { useEffect, useState } from 'react'
import { Pencil, Save, X } from 'lucide-react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

type Customer = {
  id: number
  name: string
  whatsapp_phone: string | null
}

export default function CustomersPage() {
  const [items, setItems] = useState<Customer[]>([])
  const [name, setName] = useState('')
  const [whatsappPhone, setWhatsappPhone] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editName, setEditName] = useState('')
  const [editPhone, setEditPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    const { data } = await api.get<Customer[]>('/customers/')
    setItems(data)
  }

  useEffect(() => {
    let cancelled = false

    const loadInitialCustomers = async () => {
      try {
        const { data } = await api.get<Customer[]>('/customers/')
        if (!cancelled) setItems(data)
      } catch {
        if (!cancelled) setError('Não foi possível carregar clientes.')
      }
    }

    void loadInitialCustomers()

    return () => {
      cancelled = true
    }
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/customers/', { name, whatsapp_phone: whatsappPhone })
      setName('')
      setWhatsappPhone('')
      await load()
    } catch {
      setError('Erro ao cadastrar cliente.')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async (customerId: number) => {
    setError('')
    try {
      await api.put(`/customers/${customerId}`, {
        name: editName,
        whatsapp_phone: editPhone,
      })
      setEditingId(null)
      await load()
    } catch {
      setError('Não foi possível atualizar o cliente. Verifique se o telefone já está vinculado.')
    }
  }

  const startEditing = (customer: Customer) => {
    setEditingId(customer.id)
    setEditName(customer.name)
    setEditPhone(customer.whatsapp_phone ?? '')
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
          <form className="grid gap-3 md:grid-cols-[1fr_1fr_auto]" onSubmit={handleCreate}>
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
            <div className="space-y-1">
              <Label htmlFor="whatsapp-phone">WhatsApp do cliente</Label>
              <Input
                id="whatsapp-phone"
                type="tel"
                value={whatsappPhone}
                onChange={(e) => setWhatsappPhone(e.target.value)}
                placeholder="+55 11 99999-8888"
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
                  <th className="py-2">WhatsApp</th>
                  <th className="py-2">Ações</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b">
                    <td className="py-2">{item.id}</td>
                    <td className="py-2">
                      {editingId === item.id ? (
                        <Input value={editName} onChange={(e) => setEditName(e.target.value)} aria-label="Nome do cliente" />
                      ) : item.name}
                    </td>
                    <td className="py-2">
                      {editingId === item.id ? (
                        <Input type="tel" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} aria-label="Telefone WhatsApp" />
                      ) : item.whatsapp_phone || 'Não vinculado'}
                    </td>
                    <td className="py-2">
                      <div className="flex gap-2">
                        {editingId === item.id ? (
                          <>
                            <Button type="button" variant="outline" size="icon" onClick={() => void handleUpdate(item.id)} aria-label="Salvar alterações" title="Salvar alterações">
                              <Save />
                            </Button>
                            <Button type="button" variant="outline" size="icon" onClick={() => setEditingId(null)} aria-label="Cancelar edição" title="Cancelar edição">
                              <X />
                            </Button>
                          </>
                        ) : (
                          <Button type="button" variant="outline" size="icon" onClick={() => startEditing(item)} aria-label="Editar cliente" title="Editar cliente">
                            <Pencil />
                          </Button>
                        )}
                        <Button type="button" variant="destructive" size="sm" onClick={() => handleDelete(item.id)}>
                          Excluir
                        </Button>
                      </div>
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
