// Barra superior: marca, pestañas de navegación y la persona con su rol.
// NavLink marca aria-current="page" en la pestaña de la ruta activa.

import { Link, NavLink } from 'react-router-dom';
import Button from './Button.jsx';
import Marca from './Marca.jsx';

// Coordinación en azul río y Analista SIG en verde dosel: el mismo código de color que la tabla de usuarios.
const COLOR_ROL = {
  Coordinación: 'text-rio',
  'Analista SIG': 'text-dosel',
};

export default function Navbar({ isAuthenticated = false, userName = 'Usuario', userRole = '', links = [], onLogin, onLogout }) {
  return (
    <header className="border-b border-linea bg-white">
      <div className="mx-auto flex min-h-16 max-w-6xl flex-wrap items-center gap-x-8 px-4 sm:px-8">
        <Link to="/dashboard" className="flex items-center gap-2.5 py-3 text-tinta no-underline">
          <Marca />
          <span className="text-lg font-bold [font-stretch:115%]">EcoAlert</span>
          <span className="text-tinta-suave">Tambopata</span>
        </Link>

        <nav aria-label="Navegación principal" className="flex grow gap-1 max-sm:order-last max-sm:w-full">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex min-h-14 items-center px-3.5 sm:min-h-16 ${
                  isActive
                    ? 'font-semibold text-tinta shadow-[inset_0_-3px_0_var(--color-dosel)]'
                    : 'font-medium text-tinta-suave hover:text-tinta'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        {isAuthenticated ? (
          <div className="ml-auto flex items-center gap-3.5 py-2.5">
            <div className="flex flex-col items-end leading-tight">
              <span className="text-sm font-semibold">{userName}</span>
              {userRole && <span className={`text-[13px] ${COLOR_ROL[userRole] ?? 'text-tinta-suave'}`}>{userRole}</span>}
            </div>
            <Button variant="secondary" onClick={onLogout} className="min-h-10 px-3.5 text-sm font-medium">
              Cerrar sesión
            </Button>
          </div>
        ) : (
          onLogin && (
            <Button variant="secondary" onClick={onLogin} className="ml-auto">
              Iniciar sesión
            </Button>
          )
        )}
      </div>
    </header>
  );
}
