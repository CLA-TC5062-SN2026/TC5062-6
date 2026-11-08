// Página de inicio de sesión (RF-01): formulario → authService.login() → token guardado → redirección.

import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import Card from '../components/Card.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import { useAuth } from '../context/AuthContext.jsx';

const RUTA_INICIAL = '/dashboard';
const FORMATO_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// Mismo tope que el contrato para la contraseña del login (CredencialesLogin.password).
const MAX_PASSWORD = 1024;

/** Solo se vuelve a rutas internas de la SPA: evita redirecciones abiertas a otros dominios. */
function rutaDeRetorno(state) {
  const ruta = state?.from?.pathname;
  const esInterna = typeof ruta === 'string' && ruta.startsWith('/') && !ruta.startsWith('//');
  return esInterna && ruta !== '/login' ? `${ruta}${state.from.search ?? ''}` : RUTA_INICIAL;
}

function validar({ correo, password }) {
  const errores = {};
  if (!correo.trim()) errores.correo = 'Ingresa tu correo electrónico.';
  else if (!FORMATO_CORREO.test(correo.trim())) errores.correo = 'Ingresa un correo electrónico válido.';
  if (!password) errores.password = 'Ingresa tu contraseña.';
  else if (password.length > MAX_PASSWORD) errores.password = 'La contraseña es demasiado larga.';
  return errores;
}

export default function LoginPage() {
  const { estaAutenticado, login, aviso } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ correo: '', password: '' });
  const [errores, setErrores] = useState({});
  const [errorServidor, setErrorServidor] = useState(null);
  const [enviando, setEnviando] = useState(false);

  if (estaAutenticado && !enviando) {
    return <Navigate to={rutaDeRetorno(location.state)} replace />;
  }

  function actualizar(campo) {
    return (event) => setForm((previo) => ({ ...previo, [campo]: event.target.value }));
  }

  async function enviar(event) {
    event.preventDefault();
    const encontrados = validar(form);
    setErrores(encontrados);
    setErrorServidor(null);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    try {
      await login(form);
      navigate(rutaDeRetorno(location.state), { replace: true });
    } catch (error) {
      // El mensaje ya viene listo para el usuario desde la capa de servicios (ApiError).
      setErrorServidor(error.message);
      setForm((previo) => ({ ...previo, password: '' }));
      setEnviando(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-100 px-4 py-12">
      <div className="w-full max-w-md">
        <p className="mb-2 text-center text-sm font-semibold uppercase tracking-widest text-green-800">
          EcoAlert Tambopata
        </p>
        <Card title="Iniciar sesión" headingLevel={1}>
          <form noValidate onSubmit={enviar} className="flex flex-col gap-4" aria-describedby="aviso-login">
            <div id="aviso-login" className="flex flex-col gap-3">
              {aviso && !errorServidor && (
                <ErrorAlert titulo="Tu sesión terminó" mensaje={aviso} />
              )}
              <ErrorAlert titulo="No se pudo iniciar sesión" mensaje={errorServidor} />
            </div>

            <Input
              label="Correo electrónico"
              type="email"
              name="correo"
              autoComplete="username"
              inputMode="email"
              value={form.correo}
              onChange={actualizar('correo')}
              placeholder="nombre@ecoalert.pe"
              error={errores.correo}
              required
            />

            <Input
              label="Contraseña"
              type="password"
              name="password"
              autoComplete="current-password"
              value={form.password}
              onChange={actualizar('password')}
              error={errores.password}
              maxLength={MAX_PASSWORD}
              required
            />

            <Button type="submit" loading={enviando}>
              Ingresar
            </Button>
          </form>
        </Card>
      </div>
    </main>
  );
}
