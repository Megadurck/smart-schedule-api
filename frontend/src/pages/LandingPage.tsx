import { ArrowRight, CalendarCheck2, ShieldCheck, Sparkles, Star, Users } from 'lucide-react'
import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Agendamentos Online',
    description:
      'Clientes marcam horários com validação inteligente de disponibilidade em tempo real.',
    icon: CalendarCheck2,
  },
  {
    title: 'Gestão de Profissionais',
    description:
      'Organize equipes, serviços e responsabilidades com visão clara de cada atendimento.',
    icon: Users,
  },
  {
    title: 'Controle de Horários',
    description:
      'Configure dias, slots e regras de funcionamento para evitar conflitos e sobreposição.',
    icon: Star,
  },
  {
    title: 'Segurança e Isolamento',
    description:
      'Cada empresa fica separada por tenant, mantendo dados e permissões em contexto correto.',
    icon: ShieldCheck,
  },
  {
    title: 'Assistente Inteligente',
    description:
      'Use IA para responder dúvidas, confirmar horários e agilizar processos com linguagem natural.',
    icon: Sparkles,
  },
  {
    title: 'Multi-empresa (SaaS)',
    description:
      'Escale para diversos clientes e mantenha o produto pronto para crescer com a operação.',
    icon: ArrowRight,
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(62%_34%_at_50%_-5%,rgba(181,126,67,0.2),transparent_68%),linear-gradient(180deg,#f8f2e7_0%,#efe5d6_100%)] text-foreground dark:bg-[radial-gradient(58%_30%_at_50%_-4%,rgba(181,126,67,0.24),transparent_70%),linear-gradient(180deg,#090b10_0%,#11141b_55%,#151922_100%)]">
      <div className="mx-auto max-w-7xl px-4 pb-20 pt-10 sm:px-6 lg:px-8">
        <header className="mb-16 flex items-center justify-between rounded-full border border-white/45 bg-white/65 px-4 py-3 shadow-lg shadow-amber-800/5 backdrop-blur-md dark:border-zinc-700/70 dark:bg-zinc-900/45">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-linear-to-br from-zinc-900 to-amber-700 text-sm font-bold text-amber-50 shadow-lg shadow-amber-700/20 dark:from-zinc-700 dark:to-amber-600">
              S
            </div>
            <div>
              <p className="text-sm font-semibold tracking-[0.2em] text-zinc-600 dark:text-zinc-300">
                SMART SCHEDULE
              </p>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm text-zinc-600 md:flex dark:text-zinc-300">
            <a href="#features" className="transition hover:text-zinc-900 dark:hover:text-zinc-100">
              Recursos
            </a>
            <a href="#benefits" className="transition hover:text-zinc-900 dark:hover:text-zinc-100">
              Benefícios
            </a>
          </nav>
        </header>

        <section className="grid items-center gap-10 pb-12 pt-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div>
            <h1 className="max-w-xl text-4xl font-black tracking-tight text-zinc-900 sm:text-5xl lg:text-6xl dark:text-zinc-100">
              Agendamento inteligente para negócios que querem crescer.
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-zinc-600 dark:text-zinc-300">
              Centralize clientes, profissionais, horários e atendimento em uma experiência moderna,
              rápida e com suporte inteligente por IA.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-linear-to-r from-zinc-900 via-zinc-800 to-amber-700 px-6 py-3 text-sm font-semibold text-amber-50 shadow-lg shadow-amber-700/25 transition hover:scale-[1.01] dark:from-zinc-700 dark:to-amber-600"
              >
                Cadastrar minha empresa
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center justify-center rounded-full border border-zinc-300/70 bg-white/75 px-6 py-3 text-sm font-semibold text-zinc-700 shadow-sm transition hover:border-zinc-400/70 hover:bg-white dark:border-zinc-700 dark:bg-zinc-900/60 dark:text-zinc-200"
              >
                Já tenho acesso
              </Link>
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-6 text-sm text-zinc-500 dark:text-zinc-300">
              <span>+ 90% menos retrabalho manual</span>
              <span>•</span>
              <span>Interface moderna</span>
              <span>•</span>
              <span>IA local</span>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -left-10 top-8 h-48 w-48 rounded-full bg-amber-400/20 blur-3xl" />
            <div className="absolute -right-6 bottom-4 h-52 w-52 rounded-full bg-orange-400/15 blur-3xl" />

            <div className="relative overflow-hidden rounded-[28px] border border-zinc-300/60 bg-white/75 p-5 shadow-[0_30px_80px_rgba(89,64,31,0.24)] backdrop-blur-xl dark:border-zinc-700 dark:bg-zinc-900/70">
              <div className="rounded-2xl border border-zinc-300/55 bg-stone-50 p-4 dark:border-zinc-700 dark:bg-zinc-950/70">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-zinc-400">Overview</p>
                    <p className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Agenda</p>
                  </div>
                  <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
                    Em dia
                  </span>
                </div>

                <div className="space-y-3">
                  {[
                    ['09:00', 'Corte de cabelo', 'Lucas'],
                    ['11:30', 'Manicure', 'Patrícia'],
                    ['14:00', 'Barba', 'João'],
                  ].map(([time, service, person]) => (
                    <div
                      key={time}
                      className="flex items-center justify-between rounded-2xl border border-zinc-200 bg-white p-3 dark:border-zinc-700 dark:bg-zinc-900"
                    >
                      <div>
                        <p className="text-xs text-zinc-400">{time}</p>
                        <p className="font-medium text-zinc-900 dark:text-zinc-100">{service}</p>
                      </div>
                      <span className="text-sm text-zinc-500 dark:text-zinc-300">{person}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="pt-10">
          <div className="mb-8 max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-amber-700 dark:text-amber-300">
              Recursos
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
              Tudo que seu negócio precisa para operar com eficiência.
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {features.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="rounded-2xl border border-zinc-300/60 bg-white/70 p-5 shadow-sm backdrop-blur-sm transition hover:-translate-y-1 hover:shadow-xl dark:border-zinc-700 dark:bg-zinc-900/60"
              >
                <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-linear-to-br from-zinc-900 to-amber-700 text-amber-50 shadow-md shadow-amber-700/20 dark:from-zinc-700 dark:to-amber-600">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-300">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section id="benefits" className="mt-16 rounded-[28px] border border-zinc-200/70 bg-linear-to-r from-zinc-900 via-zinc-800 to-amber-900 p-8 text-amber-50 shadow-[0_30px_80px_rgba(17,12,6,0.38)] dark:border-zinc-700">
          <div className="grid gap-8 lg:grid-cols-[1fr_0.8fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-amber-200">
                Por que escolher
              </p>
              <h2 className="mt-3 text-3xl font-bold">Comodidade para quem atende e previsibilidade para quem administra.</h2>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <p className="text-amber-100/90">
                O Smart Schedule combina gestão operacional, autonomia de agendamento e assistente de IA em uma mesma experiência, reduzindo erros, atrasos e fricção do atendimento.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
