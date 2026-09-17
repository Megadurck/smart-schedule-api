import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/useAuth'
import { useState } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

const schema = z.object({
  company_name: z.string().min(1, 'Informe o nome da empresa'),
  user_name: z.string().min(1, 'Informe o usuário'),
  password: z.string().min(6, 'Mínimo 6 caracteres'),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const justRegistered = (location.state as { registered?: boolean } | null)?.registered === true
  const [serverError, setServerError] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setServerError('')
    try {
      await login(data.company_name, data.user_name, data.password)
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Credenciais inválidas.'
      setServerError(msg)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(60%_34%_at_50%_-5%,rgba(181,126,67,0.2),transparent_68%),linear-gradient(180deg,#f8f2e7_0%,#efe5d6_100%)] px-4 py-8 dark:bg-[radial-gradient(56%_30%_at_50%_-4%,rgba(181,126,67,0.24),transparent_70%),linear-gradient(180deg,#090b10_0%,#11141b_55%,#151922_100%)]">
      <Card className="w-full max-w-md overflow-hidden border border-zinc-300/70 bg-white/80 shadow-[0_30px_80px_rgba(89,64,31,0.18)] backdrop-blur-xl dark:border-zinc-700 dark:bg-zinc-900/80 dark:shadow-[0_30px_80px_rgba(4,6,12,0.5)]">
        <div className="bg-linear-to-r from-zinc-900 via-zinc-800 to-amber-700 px-6 py-6 text-amber-50 dark:from-zinc-700 dark:to-amber-600">
          <p className="text-xs font-medium uppercase tracking-[0.28em] text-amber-100">Smart Schedule</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">Bem-vindo</h1>
        </div>

        <CardHeader className="space-y-1 px-6 pt-6">
          <CardTitle className="text-center text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            Acesse sua conta
          </CardTitle>
          <CardDescription className="text-center text-zinc-600 dark:text-zinc-300">
            Gerencie horários, clientes e profissionais em um só lugar.
          </CardDescription>
        </CardHeader>

        {justRegistered && (
          <div className="mx-6 mb-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-center text-sm text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300">
            Empresa cadastrada com sucesso! Faça o login para continuar.
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <CardContent className="space-y-4 px-6 pb-2">
            <div className="space-y-2">
              <Label htmlFor="company_name" className="text-sm font-medium text-zinc-700 dark:text-zinc-200">
                Empresa
              </Label>
              <Input
                id="company_name"
                placeholder="Nome da empresa"
                className="h-11 rounded-xl border-zinc-200 bg-stone-50 dark:border-zinc-700 dark:bg-zinc-950/60"
                {...register('company_name')}
              />
              {errors.company_name && (
                <p className="text-sm text-red-500">{errors.company_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="user_name" className="text-sm font-medium text-zinc-700 dark:text-zinc-200">
                Usuário
              </Label>
              <Input
                id="user_name"
                placeholder="Seu usuário"
                className="h-11 rounded-xl border-zinc-200 bg-stone-50 dark:border-zinc-700 dark:bg-zinc-950/60"
                {...register('user_name')}
              />
              {errors.user_name && (
                <p className="text-sm text-red-500">{errors.user_name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-zinc-700 dark:text-zinc-200">
                Senha
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••"
                className="h-11 rounded-xl border-zinc-200 bg-stone-50 dark:border-zinc-700 dark:bg-zinc-950/60"
                {...register('password')}
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            {serverError && (
              <p className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300">
                {serverError}
              </p>
            )}
          </CardContent>

          <CardFooter className="flex flex-col gap-3 px-6 pb-6 pt-4">
            <Button type="submit" className="h-11 w-full rounded-xl bg-linear-to-r from-zinc-900 to-amber-700 text-amber-50 shadow-lg shadow-amber-700/20 dark:from-zinc-700 dark:to-amber-600" disabled={isSubmitting}>
              {isSubmitting ? 'Entrando…' : 'Entrar'}
            </Button>
            <Link to="/" className="text-center text-sm text-muted-foreground hover:underline">
              ← Voltar à página inicial
            </Link>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
