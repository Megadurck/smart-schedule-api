import { Link } from 'react-router-dom'

const features = [
  {
    title: 'Agendamentos Online',
    description:
      'Clientes agendam horários diretamente pelo sistema, com validação de disponibilidade em tempo real.',
  },
  {
    title: 'Gestão de Profissionais',
    description:
      'Cadastre e gerencie os profissionais da sua empresa, vinculando cada agendamento ao responsável pelo atendimento.',
  },
  {
    title: 'Controle de Horários',
    description:
      'Configure os dias e horários de funcionamento por profissional para evitar conflitos de agenda.',
  },
  {
    title: 'Cadastro de Clientes',
    description:
      'Mantenha um histórico completo dos seus clientes com dados de contato e agendamentos anteriores.',
  },
  {
    title: 'Assistente Inteligente',
    description:
      'Agente de IA integrado para responder dúvidas e auxiliar na gestão dos agendamentos via linguagem natural.',
  },
  {
    title: 'Multi-empresa (SaaS)',
    description:
      'Cada empresa possui seus dados completamente isolados. Segurança e privacidade garantidas por design.',
  },
]

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <header>
        <h1>Smart Schedule</h1>
        <p>
          A plataforma de agendamentos inteligente para negócios que não param. Organize sua agenda,
          reduza faltas e atenda mais com menos esforço.
        </p>
        <nav>
          <Link to="/register">Cadastrar minha empresa</Link>
          <Link to="/login">Já tenho acesso — Entrar</Link>
        </nav>
      </header>

      {/* Features */}
      <main>
        <section>
          <h2>O que o Smart Schedule oferece</h2>
          <ul>
            {features.map((feature) => (
              <li key={feature.title}>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </li>
            ))}
          </ul>
        </section>

        {/* CTA final */}
        <section>
          <h2>Pronto para começar?</h2>
          <p>
            Crie a conta da sua empresa gratuitamente e comece a gerenciar seus agendamentos agora
            mesmo.
          </p>
          <Link to="/register">Cadastrar empresa</Link>
        </section>
      </main>

      <footer>
        <p>Smart Schedule &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  )
}
