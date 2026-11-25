// Estructura común de las vistas autenticadas: barra de navegación y contenido de la ruta activa.

import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import Navbar from './Navbar.jsx';

const ENLACES = [
  { to: '/dashboard', label: 'Panel' },
  { to: '/alertas', label: 'Alertas' },
];
// RF-02-AC-10: la gestión de usuarios solo aparece en el menú de Coordinación (el backend responde 403 al resto).
const ENLACES_COORDINACION = [{ to: '/usuarios', label: 'Usuarios' }];

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
        links={usuario?.rol === 'coordinacion' ? [...ENLACES, ...ENLACES_COORDINACION] : ENLACES}
        onLogout={cerrarSesion}
      />
      <main id="contenido" className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
