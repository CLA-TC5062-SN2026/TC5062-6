import { Link } from 'react-router-dom';
import Marca from '../components/Marca.jsx';

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-papel px-4 text-center">
      <Marca tamano={40} />
      <h1 className="ancho-titulo text-4xl font-bold">Página no encontrada</h1>
      <p className="text-tinta-suave">Esta dirección no existe en EcoAlert.</p>
      <Link to="/" className="font-semibold text-dosel underline underline-offset-4">
        Ir al panel
      </Link>
    </main>
  );
}
