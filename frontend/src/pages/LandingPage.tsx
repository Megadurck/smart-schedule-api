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
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(129,140,248,0.22),transparent_18%),linear-gradient(180deg,#f8fafc_0%,#eef2ff_100%)] text-foreground dark:bg-[radial-gradient(circle_at_top,rgba(129,140,248,0.2),transparent_16%),linear-gradient(180deg,#020817_0%,#0f172a_100%)]">
      <div className="mx-auto max-w-7xl px-4 pb-20 pt-10 sm:px-6 lg:px-8">
        <header className="mb-16 flex items-center justify-between rounded-full border border-white/30 bg-white/60 px-4 py-3 shadow-lg shadow-indigo-500/5 backdrop-blur-md dark:border-slate-700/60 dark:bg-slate-900/40">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-linear-to-br from-indigo-600 to-violet-500 text-sm font-bold text-white shadow-lg shadow-indigo-500/30">
              S
            </div>
            <div>
              <p className="text-sm font-semibold tracking-[0.2em] text-slate-500 dark:text-slate-300">
                SMART SCHEDULE
              </p>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm text-slate-600 md:flex dark:text-slate-300">
            <a href="#features" className="transition hover:text-slate-900 dark:hover:text-white">
              Recursos
            </a>
            <a href="#benefits" className="transition hover:text-slate-900 dark:hover:text-white">
              Benefícios
            </a>
          </nav>
        </header>

        <section className="grid items-center gap-10 pb-12 pt-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div>
            <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 dark:border-indigo-500/40 dark:bg-indigo-500/10 dark:text-indigo-200">
              <Sparkles className="h-3.5 w-3.5" />
              Plataforma premium para agendamento profissional
            </span>

            <h1 className="max-w-xl text-4xl font-black tracking-tight text-slate-900 sm:text-5xl lg:text-6xl dark:text-white">
              Agendamento inteligente para negócios que querem crescer.
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Centralize clientes, profissionais, horários e atendimento em uma experiência moderna,
              rápida e com suporte inteligente por IA.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-linear-to-r from-indigo-600 to-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01]"
              >
                Cadastrar minha empresa
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white/80 px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-white dark:border-slate-700 dark:bg-slate-900/60 dark:text-slate-200"
              >
                Já tenho acesso
              </Link>
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-6 text-sm text-slate-500 dark:text-slate-300">
              <span>+ 90% menos retrabalho manual</span>
              <span>•</span>
              <span>Interface moderna</span>
              <span>•</span>
              <span>IA local</span>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -left-10 top-8 h-48 w-48 rounded-full bg-violet-400/20 blur-3xl" />
            <div className="absolute -right-6 bottom-4 h-52 w-52 rounded-full bg-indigo-400/20 blur-3xl" />

            <div className="relative overflow-hidden rounded-[28px] border border-slate-200 bg-white/70 p-5 shadow-[0_30px_80px_rgba(79,70,229,0.22)] backdrop-blur-xl dark:border-slate-700 dark:bg-slate-900/70">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950/70">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Overview</p>
                    <p className="text-xl font-semibold text-slate-900 dark:text-white">Agenda</p>
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
                      className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-900"
                    >
                      <div>
                        <p className="text-xs text-slate-400">{time}</p>
                        <p className="font-medium text-slate-900 dark:text-white">{service}</p>
                      </div>
                      <span className="text-sm text-slate-500 dark:text-slate-300">{person}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="pt-10">
          <div className="mb-8 max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600 dark:text-indigo-300">
              Recursos
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Tudo que seu negócio precisa para operar com eficiência.
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {features.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="rounded-2xl border border-slate-200 bg-white/70 p-5 shadow-sm backdrop-blur-sm transition hover:-translate-y-1 hover:shadow-xl dark:border-slate-700 dark:bg-slate-900/60"
              >
                <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-linear-to-br from-indigo-500 to-violet-500 text-white shadow-md shadow-indigo-500/20">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
                  {description}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section id="benefits" className="mt-16 rounded-[28px] border border-slate-200 bg-linear-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 text-white shadow-[0_30px_80px_rgba(15,23,42,0.35)]">
          <div className="grid gap-8 lg:grid-cols-[1fr_0.8fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-indigo-200">
                Por que escolher
              </p>
              <h2 className="mt-3 text-3xl font-bold">Comodidade para quem atende e previsibilidade para quem administra.</h2>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <p className="text-slate-200">
                O Smart Schedule combina gestão operacional, autonomia de agendamento e assistente de IA em uma mesma experiência, reduzindo erros, atrasos e fricção do atendimento.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
