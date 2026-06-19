import { Link } from 'react-router-dom'

const APP_NAME = 'Sistema Web'

interface Recurso {
  icone: string
  cor: string
  titulo: string
  texto: string
}

const recursos: Recurso[] = [
  {
    icone: 'bi-shield-check',
    cor: 'text-primary',
    titulo: 'Segurança',
    texto: 'Sistema seguro com autenticação robusta e criptografia de dados',
  },
  {
    icone: 'bi-person-circle',
    cor: 'text-info',
    titulo: 'Perfil Personalizável',
    texto: 'Personalize seu perfil com foto e informações pessoais',
  },
  {
    icone: 'bi-speedometer2',
    cor: 'text-warning',
    titulo: 'Rápido e Responsivo',
    texto: 'Interface moderna que funciona em qualquer dispositivo',
  },
  {
    icone: 'bi-bell',
    cor: 'text-danger',
    titulo: 'Notificações',
    texto: 'Receba alertas e notificações sobre suas atividades',
  },
  {
    icone: 'bi-gear',
    cor: 'text-secondary',
    titulo: 'Configurável',
    texto: 'Ajuste o sistema de acordo com suas preferências',
  },
]

interface Faq {
  id: string
  pergunta: string
  resposta: string
}

const faqs: Faq[] = [
  {
    id: 'faq1',
    pergunta: 'Como criar uma conta?',
    resposta:
      'Basta clicar em "Criar Conta" no menu superior, preencher seus dados e confirmar. O processo é rápido e gratuito!',
  },
  {
    id: 'faq2',
    pergunta: 'O sistema é seguro?',
    resposta:
      'Sim! Utilizamos criptografia de ponta e as melhores práticas de segurança para proteger seus dados. Suas senhas são armazenadas de forma segura e nunca são expostas.',
  },
  {
    id: 'faq3',
    pergunta: 'Posso alterar meus dados depois?',
    resposta:
      'Claro! Você pode atualizar seus dados pessoais, foto de perfil e senha a qualquer momento através da seção "Meu Perfil" no seu dashboard.',
  },
  {
    id: 'faq4',
    pergunta: 'Esqueci minha senha, o que fazer?',
    resposta:
      'Na tela de login, clique em "Esqueci minha senha" e siga as instruções. Você receberá um e-mail com um link para redefinir sua senha.',
  },
]

export default function HomePage() {
  return (
    <>
      {/* Hero Section */}
      <div className="mb-5">
        <div className="bg-primary text-white rounded-4 shadow-lg p-5 pb-3">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h1 className="display-4 fw-bold mb-4">Bem-vindo ao {APP_NAME}</h1>
              <p className="lead mb-4">
                Uma plataforma completa e moderna para gerenciar suas atividades de forma simples e
                eficiente.
              </p>
              <div className="d-flex gap-3 flex-column flex-sm-row">
                <Link to="/cadastrar" className="btn btn-light btn-lg">
                  <i className="bi bi-person-plus" /> Criar Conta
                </Link>
                <Link to="/sobre" className="btn btn-outline-light btn-lg">
                  <i className="bi bi-info-circle" /> Saiba mais
                </Link>
              </div>
            </div>
            <div className="col-lg-6 text-center mt-4 mt-lg-0">
              <i className="bi bi-laptop display-1 opacity-25" style={{ fontSize: '8rem' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Recursos Section */}
      <div className="mb-5" id="recursos">
        <div className="text-center mb-5">
          <h2 className="fw-bold">Recursos Principais</h2>
          <p className="text-muted">Tudo que você precisa em um só lugar</p>
        </div>

        <div className="row g-4">
          {recursos.map((recurso) => (
            <div className="col-md-4" key={recurso.titulo}>
              <div className="card h-100 shadow-sm shadow-hover text-center">
                <div className="card-body p-4">
                  <div className="mb-3">
                    <i className={`bi ${recurso.icone} ${recurso.cor} display-3`} />
                  </div>
                  <h5 className="card-title">{recurso.titulo}</h5>
                  <p className="card-text text-muted">{recurso.texto}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="mb-5">
        <div className="card bg-primary text-white shadow-lg shadow-hover">
          <div className="card-body text-center p-5">
            <h2 className="fw-bold mb-4">Pronto para começar?</h2>
            <p className="lead mb-4">Crie sua conta gratuitamente e comece a usar agora mesmo!</p>
            <div className="d-flex justify-content-center gap-3 flex-column flex-sm-row">
              <Link to="/cadastrar" className="btn btn-light btn-lg">
                <i className="bi bi-person-plus" /> Criar Conta Grátis
              </Link>
              <Link to="/login" className="btn btn-outline-light btn-lg">
                <i className="bi bi-box-arrow-in-right" /> Já tenho conta
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mb-5">
        <div className="text-center mb-5">
          <h2 className="fw-bold">Perguntas Frequentes</h2>
          <p className="text-muted">Tire suas dúvidas sobre o sistema</p>
        </div>

        <div className="row">
          <div className="col-lg-8 mx-auto">
            <div className="accordion" id="faqAccordion">
              {faqs.map((faq, indice) => (
                <div className="accordion-item" key={faq.id}>
                  <h2 className="accordion-header">
                    <button
                      className={`accordion-button${indice === 0 ? '' : ' collapsed'}`}
                      type="button"
                      data-bs-toggle="collapse"
                      data-bs-target={`#${faq.id}`}
                      aria-expanded={indice === 0}
                      aria-controls={faq.id}
                    >
                      {faq.pergunta}
                    </button>
                  </h2>
                  <div
                    id={faq.id}
                    className={`accordion-collapse collapse${indice === 0 ? ' show' : ''}`}
                    data-bs-parent="#faqAccordion"
                  >
                    <div className="accordion-body">{faq.resposta}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
