
import { NavLink } from "react-router-dom";
import Button from "./Button";

const linkStyles = `
  rounded px-2 py-1
  hover:underline
  focus-visible:outline
  focus-visible:outline-2
  focus-visible:outline-offset-2
  focus-visible:outline-white
`;

export default function Navbar({
  isAuthenticated = false,
  userName = "Usuario",
  links = [],
  onLogin,
  onLogout,
}) {
  return (
    <nav
      aria-label="Navegación principal"
      className="bg-green-800 px-4 py-4 text-white sm:px-6"
    >
      <div
        className="
          mx-auto flex max-w-5xl flex-col
          gap-4 sm:flex-row sm:items-center
          sm:justify-between
        "
      >
        <span className="text-xl font-bold">
          EcoAlert Tambopata
        </span>

        <div
          className="
            flex flex-wrap items-center
            gap-3 sm:gap-4
          "
        >
          {/* NavLink marca aria-current="page" en el enlace de la ruta activa. */}
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `${linkStyles} ${isActive ? "font-semibold underline" : ""}`
              }
            >
              {link.label}
            </NavLink>
          ))}

          {isAuthenticated ? (
            <>
              <span className="text-sm">
                Hola, {userName}
              </span>

              <Button
                variant="secondary"
                onClick={onLogout}
              >
                Cerrar sesión
              </Button>
            </>
          ) : (
            onLogin && (
              <Button
                variant="secondary"
                onClick={onLogin}
              >
                Iniciar sesión
              </Button>
            )
          )}
        </div>
      </div>
    </nav>
  );
}
