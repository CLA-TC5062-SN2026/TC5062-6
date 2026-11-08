import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-gray-100 px-4 text-center">
      <h1 className="text-3xl font-bold text-green-800">Página no encontrada</h1>
      <p className="text-gray-700">La dirección que buscas no existe.</p>
      <Link to="/" className="font-medium text-green-800 underline">
        Volver al inicio
      </Link>
    </main>
  );
}
