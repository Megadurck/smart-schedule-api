import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { api } from '@/services/api'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

const schema = z
  .object({
    company_name: z.string().min(1, 'Informe o nome da empresa'),
    user_name: z.string().min(1, 'Informe o usuário'),
    password: z.string().min(6, 'Mínimo 6 caracteres'),
    confirm_password: z.string().min(6, 'Confirme a senha'),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: 'As senhas não coincidem',
    path: ['confirm_password'],
  })

type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setServerError('')
    try {
      await api.post('/auth/register', {
        company_name: data.company_name,
        user_name: data.user_name,
        password: data.password,
      })
      navigate('/login', { state: { registered: true } })
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Erro ao criar conta.'
      setServerError(msg)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.22),_transparent_18%),linear-gradient(180deg,_#f8fafc_0%,_#eef2ff_100%)] px-4 py-8 dark:bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.2),_transparent_16%),linear-gradient(180deg,_#020817_0%,_#0f172a_100%)]">
      <Card className="w-full max-w-md overflow-hidden border border-slate-200/80 bg-white/80 shadow-[0_30px_80px_rgba(79,70,229,0.15)] backdrop-blur-xl dark:border-slate-700 dark:bg-slate-900/80 dark:shadow-[0_30px_80px_rgba(2,6,23,0.45)]">
        <div className="bg-gradient-to-r from-indigo-600 via-violet-600 to-sky-500 px-6 py-6 text-white">
          <p className="text-xs font-medium uppercase tracking-[0.28em] text-indigo-100">Smart Schedule</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">Comece agora</h1>
        </div>

        <CardHeader className="space-y-1 px-6 pt-6">
          <CardTitle className="text-center text-2xl font-bold text-slate-900 dark:text-white">
            Cadastre sua empresa
          </CardTitle>
          <CardDescription className="text-center text-slate-600 dark:text-slate-300">
            Crie o primeiro acesso e organize a operação do seu negócio.
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <CardContent className="space-y-4 px-6 pb-2">
            <div className="space-y-2">
              <Label htmlFor="company_name" className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Nome da empresa
              </Label>
              <Input
                id="company_name"
                placeholder="Ex.: Barbearia do João"
                className="h-11 rounded-xl border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950/60"
                {...register('company_name')}
              />
              {errors.company_name && (
                <p className="text-sm text-red-500">{errors.company_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="user_name" className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Usuário (administrador)
              </Label>
              <Input
                id="user_name"
                placeholder="admin"
                className="h-11 rounded-xl border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950/60"
                {...register('user_name')}
              />
              {errors.user_name && (
                <p className="text-sm text-red-500">{errors.user_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Senha
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••"
                className="h-11 rounded-xl border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950/60"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm_password" className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Confirmar senha
              </Label>
              <Input
                id="confirm_password"
                type="password"
                placeholder="••••••"
                className="h-11 rounded-xl border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950/60"
                {...register('confirm_password')}
              />
              {errors.confirm_password && (
                <p className="text-sm text-red-500">{errors.confirm_password.message}</p>
              )}
            </div>

            {serverError && (
              <p className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300">
                {serverError}
              </p>
            )}
          </CardContent>

          <CardFooter className="flex flex-col gap-3 px-6 pb-6 pt-4">
            <Button type="submit" className="h-11 w-full rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/20" disabled={isSubmitting}>
              {isSubmitting ? 'Criando conta…' : 'Criar conta'}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              Já tem conta?{' '}
              <Link to="/login" className="font-medium text-indigo-600 hover:underline dark:text-indigo-300">
                Fazer login
              </Link>
            </p>
            <Link to="/" className="text-center text-sm text-muted-foreground hover:underline">
              ← Voltar à página inicial
            </Link>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
