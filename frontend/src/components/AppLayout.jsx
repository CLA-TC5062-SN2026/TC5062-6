// Estructura común de las vistas autenticadas: barra de navegación y contenido de la ruta activa.

import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import Navbar from './Navbar.jsx';

const ENLACES = [
  { to: '/dashboard', label: 'Panel' },
  { to: '/alertas', label: 'Alertas' },
];

export default function AppLayout() {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();

  async function cerrarSesion() {
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar
        isAuthenticated
        userName={usuario?.nombre_completo}
        links={ENLACES}
        onLogout={cerrarSesion}
      />
      <main id="contenido" className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
