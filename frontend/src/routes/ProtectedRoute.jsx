// Ruta protegida: solo muestra su contenido con una sesión confirmada.
// Sin sesión redirige a /login y recuerda la ruta pedida para volver a ella después de iniciar sesión.
// Es una protección de experiencia de usuario: la autorización real la aplica el backend en cada petición.

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import LoadingState from '../components/LoadingState.jsx';
import { ESTADO_SESION, useAuth } from '../context/AuthContext.jsx';

export default function ProtectedRoute({ children }) {
  const { estado } = useAuth();
  const location = useLocation();

  if (estado === ESTADO_SESION.VERIFICANDO) {
    return <LoadingState mensaje="Verificando tu sesión…" pantallaCompleta />;
  }
  if (estado !== ESTADO_SESION.AUTENTICADO) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children ?? <Outlet />;
}
