export default function Footer() {
  const ano = new Date().getFullYear()
  return (
    <footer className="bg-light text-center text-muted py-3 mt-auto">
      <div className="container">
        <p className="mb-0">&copy; {ano} Sistema Web. Todos os direitos reservados.</p>
      </div>
    </footer>
  )
}
