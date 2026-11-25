// Estructura común de las vistas autenticadas: barra superior y contenido de la ruta activa.

import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import Navbar from './Navbar.jsx';

const ENLACES = [
  { to: '/dashboard', label: 'Panel' },
  { to: '/alertas', label: 'Alertas' },
];
// RF-02-AC-10: la gestión de usuarios solo aparece en el menú de Coordinación (el backend responde 403 al resto).
const ENLACES_COORDINACION = [{ to: '/usuarios', label: 'Usuarios' }];

const ROLES = {
  analista_sig: 'Analista SIG',
  coordinacion: 'Coordinación',
};

export default function AppLayout() {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();

  async function cerrarSesion() {
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="min-h-screen bg-papel">
      <Navbar
        isAuthenticated
        userName={usuario?.nombre_completo}
        userRole={ROLES[usuario?.rol] ?? ''}
        links={usuario?.rol === 'coordinacion' ? [...ENLACES, ...ENLACES_COORDINACION] : ENLACES}
        onLogout={cerrarSesion}
      />
      <main id="contenido" className="mx-auto flex max-w-6xl flex-col gap-6 px-4 pt-9 pb-16 sm:px-8">
        <Outlet />
      </main>
    </div>
  );
}
