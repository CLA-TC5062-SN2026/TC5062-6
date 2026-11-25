// Página de inicio de sesión (RF-01): formulario → authService.login() → token guardado → redirección.

import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import Marca from '../components/Marca.jsx';
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
  const [verPassword, setVerPassword] = useState(false);

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
    <main className="flex min-h-screen flex-wrap bg-papel">
      <PortadaCartografica />

      <section className="flex flex-[1_1_420px] items-center justify-center px-6 py-12">
        <form noValidate onSubmit={enviar} className="flex w-full max-w-sm flex-col gap-5" aria-describedby="aviso-login">
          <h1 className="ancho-titulo text-3xl leading-tight font-bold">Iniciar sesión</h1>

          <div id="aviso-login" className="flex flex-col gap-3 empty:hidden">
            {aviso && !errorServidor && <ErrorAlert titulo="Tu sesión terminó" mensaje={aviso} />}
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
            type={verPassword ? 'text' : 'password'}
            name="password"
            autoComplete="current-password"
            value={form.password}
            onChange={actualizar('password')}
            error={errores.password}
            maxLength={MAX_PASSWORD}
            required
            sufijo={
              <button
                type="button"
                onClick={() => setVerPassword((visible) => !visible)}
                aria-label={verPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                className="h-full rounded px-3.5 text-sm font-semibold text-dosel hover:bg-dosel-tenue"
              >
                {verPassword ? 'Ocultar' : 'Mostrar'}
              </button>
            }
          />

          <Button type="submit" loading={enviando} className="min-h-12 text-base">
            Ingresar
          </Button>

          <p className="text-sm text-tinta-suave">¿Sin cuenta? Pídela a Coordinación.</p>
        </form>
      </section>
    </main>
  );
}

/** Portada tipo hoja de mapa: curvas de nivel sobre verde dosel y un recuadro de título con doble marco. */
function PortadaCartografica() {
  return (
    <section className="relative flex flex-[1_1_520px] flex-col justify-end overflow-hidden bg-dosel p-6 max-sm:min-h-72 sm:p-10">
      <svg
        aria-hidden="true"
        viewBox="0 0 800 860"
        preserveAspectRatio="xMidYMid slice"
        className="absolute inset-0 h-full w-full"
        fill="none"
        stroke="#3e7259"
        strokeWidth="1.4"
      >
        {CURVAS_DE_NIVEL.map((d) => (
          <path key={d} d={d} />
        ))}
      </svg>
      <div className="relative max-w-md self-start border border-tinta bg-papel p-1.5">
        <div className="flex flex-col gap-3 border border-linea-fuerte px-7 py-6">
          <p className="flex items-center gap-3">
            <Marca tamano={34} />
            <span className="ancho-titulo text-3xl leading-none font-extrabold [font-stretch:120%]">EcoAlert</span>
          </p>
          <p className="text-[17px] leading-snug font-medium text-balance">
            Alertas de pérdida de bosque en la Reserva Nacional Tambopata, agrupadas por zona de cambio.
          </p>
          <p className="text-[13px] text-tinta-suave">Madre de Dios, Perú. Alertas de GeoBosques.</p>
        </div>
      </div>
    </section>
  );
}

// Curvas de nivel decorativas (no representan un relieve real).
const CURVAS_DE_NIVEL = [
  'M-20 140c120-40 230 10 330-20s190-110 300-80 160 70 210 60',
  'M-20 190c130-36 230 16 336-12s196-100 300-70 150 66 204 60',
  'M-20 240c140-30 236 20 342-4s200-92 300-62 146 62 198 60',
  'M-20 300c150-22 240 26 350 6s204-80 300-52 140 58 190 60',
  'M360 430c70-40 170-30 200 30s-20 130-110 140-170-30-170-90 20-60 80-80z',
  'M384 450c52-28 124-20 146 22s-16 96-80 104-124-22-124-66 14-44 58-60z',
  'M408 470c34-18 80-12 94 14s-10 60-52 66-80-14-80-42 10-28 38-38z',
  'M-20 620c110 20 200-30 290-10s150 90 250 90 200-60 300-50',
  'M-20 680c120 22 206-22 296-4s156 84 252 84 196-54 292-44',
  'M-20 740c130 24 212-14 302 2s162 78 254 78 192-48 284-38',
  'M-20 800c140 26 218-6 308 8s168 72 256 72 188-42 276-32',
];
