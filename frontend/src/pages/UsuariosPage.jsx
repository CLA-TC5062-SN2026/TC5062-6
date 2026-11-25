// Flujo de negocio: gestión de cuentas por Coordinación (RF-02). CRUD sobre /usuarios:
// crear (POST, idempotente), leer (GET), actualizar (PATCH merge-patch) y baja lógica (desactivar/reactivar).
// Las cuentas no se eliminan (RF-02-AC-7): conservar la cuenta conserva la autoría del historial de zonas.
// La autorización real la aplica el backend (403 para Analista SIG, RNF-02); aquí solo se evita mostrar
// una pantalla que no puede usar.

import { useRef, useState } from 'react';
import Button from '../components/Button.jsx';
import Card from '../components/Card.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import LoadingState from '../components/LoadingState.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { useApiQuery } from '../hooks/useApiQuery.js';
import { nuevaClaveIdempotencia, usuariosService } from '../services/usuariosService.js';

export const ROLES = {
  analista_sig: 'Analista SIG',
  coordinacion: 'Coordinación',
};

// Mismas reglas del contrato (UsuarioCrear): validar en el cliente evita un 422 evitable.
const MIN_PASSWORD = 12; // PS-15
const MAX_PASSWORD = 128;
const MAX_NOMBRE = 120;
const FORMATO_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const OPCIONES_ESTADO = [
  { valor: '', etiqueta: 'Todas' },
  { valor: 'true', etiqueta: 'Activas' },
  { valor: 'false', etiqueta: 'Desactivadas' },
];

const FORMULARIO_VACIO = { nombreCompleto: '', correo: '', rol: 'analista_sig', passwordTemporal: '' };
const CLASES_SELECT =
  'rounded-md border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-700';

const formatoFecha = new Intl.DateTimeFormat('es-PE', { dateStyle: 'medium', timeZone: 'America/Lima' });

function fechaLegible(iso) {
  const fecha = new Date(iso);
  return Number.isNaN(fecha.getTime()) ? iso : formatoFecha.format(fecha);
}

function validarNuevaCuenta({ nombreCompleto, correo, passwordTemporal }) {
  const errores = {};
  const nombre = nombreCompleto.trim();
  if (!nombre) errores.nombreCompleto = 'Ingresa el nombre completo.';
  else if (nombre.length > MAX_NOMBRE) errores.nombreCompleto = `Máximo ${MAX_NOMBRE} caracteres.`;
  if (!correo.trim()) errores.correo = 'Ingresa el correo.';
  else if (!FORMATO_CORREO.test(correo.trim())) errores.correo = 'Ingresa un correo electrónico válido.';
  if (passwordTemporal.length < MIN_PASSWORD) {
    errores.passwordTemporal = `La contraseña temporal debe tener al menos ${MIN_PASSWORD} caracteres.`;
  } else if (passwordTemporal.length > MAX_PASSWORD) {
    errores.passwordTemporal = `La contraseña temporal admite como máximo ${MAX_PASSWORD} caracteres.`;
  }
  return errores;
}

function SelectorRol({ id, value, onChange, label = 'Rol' }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-gray-700">
        {label}
      </label>
      <select id={id} value={value} onChange={onChange} className={CLASES_SELECT}>
        {Object.entries(ROLES).map(([valor, etiqueta]) => (
          <option key={valor} value={valor}>
            {etiqueta}
          </option>
        ))}
      </select>
    </div>
  );
}

function FormularioNuevaCuenta({ onCreada }) {
  const [form, setForm] = useState(FORMULARIO_VACIO);
  const [errores, setErrores] = useState({});
  const [errorServidor, setErrorServidor] = useState(null);
  const [enviando, setEnviando] = useState(false);
  // Una clave por cuerpo: si el envío falla por red y se reintenta sin cambios, se reutiliza la misma clave
  // y el servidor no crea una segunda cuenta. Si cambia cualquier campo, la clave se renueva.
  const clave = useRef(nuevaClaveIdempotencia());

  function actualizar(campo) {
    return (event) => {
      clave.current = nuevaClaveIdempotencia();
      setForm((previo) => ({ ...previo, [campo]: event.target.value }));
    };
  }

  async function enviar(event) {
    event.preventDefault();
    const encontrados = validarNuevaCuenta(form);
    setErrores(encontrados);
    setErrorServidor(null);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    try {
      const creada = await usuariosService.crear(form, { idempotencyKey: clave.current });
      clave.current = nuevaClaveIdempotencia();
      setForm(FORMULARIO_VACIO);
      onCreada(creada);
    } catch (error) {
      setErrorServidor(error.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Card title="Nueva cuenta" headingLevel={2} className="mb-6">
      <form noValidate onSubmit={enviar} className="flex flex-col gap-4">
        <ErrorAlert titulo="No se pudo crear la cuenta" mensaje={errorServidor} />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Input
            label="Nombre completo"
            name="nombre_completo"
            value={form.nombreCompleto}
            onChange={actualizar('nombreCompleto')}
            error={errores.nombreCompleto}
            maxLength={MAX_NOMBRE}
            autoComplete="off"
          />
          <Input
            label="Correo"
            type="email"
            name="correo"
            value={form.correo}
            onChange={actualizar('correo')}
            error={errores.correo}
            placeholder="nombre@ecoalert.pe"
            autoComplete="off"
          />
          <SelectorRol id="nuevo-rol" value={form.rol} onChange={actualizar('rol')} />
          <Input
            label="Contraseña temporal"
            type="password"
            name="password_temporal"
            value={form.passwordTemporal}
            onChange={actualizar('passwordTemporal')}
            error={errores.passwordTemporal}
            autoComplete="new-password"
            maxLength={MAX_PASSWORD}
          />
        </div>
        <p className="text-sm text-gray-600">
          Mínimo {MIN_PASSWORD} caracteres. La persona deberá cambiarla en su primer ingreso.
        </p>
        <div>
          <Button type="submit" loading={enviando}>
            Crear cuenta
          </Button>
        </div>
      </form>
    </Card>
  );
}

function FilaUsuario({ cuenta, esPropia, onOperar }) {
  const [modo, setModo] = useState('ver'); // ver | editar | confirmar
  const [edicion, setEdicion] = useState({ nombre_completo: cuenta.nombre_completo, rol: cuenta.rol });
  const [ocupado, setOcupado] = useState(false);

  async function operar(accion, descripcion) {
    setOcupado(true);
    const ok = await onOperar(accion, descripcion);
    setOcupado(false);
    if (ok) setModo('ver');
  }

  function guardarEdicion(event) {
    event.preventDefault();
    const cambios = {};
    const nombre = edicion.nombre_completo.trim();
    if (nombre && nombre !== cuenta.nombre_completo) cambios.nombre_completo = nombre;
    if (edicion.rol !== cuenta.rol) cambios.rol = edicion.rol;
    if (Object.keys(cambios).length === 0) {
      setModo('ver');
      return;
    }
    operar(() => usuariosService.actualizar(cuenta.id, cambios), `Cuenta de ${nombre} actualizada.`);
  }

  if (modo === 'editar') {
    return (
      <tr>
        <td colSpan={6} className="bg-green-50 px-4 py-3">
          <form onSubmit={guardarEdicion} className="grid grid-cols-1 items-end gap-3 md:grid-cols-[2fr_1fr_auto_auto]">
            <Input
              label={`Nombre de ${cuenta.correo}`}
              value={edicion.nombre_completo}
              onChange={(event) => setEdicion((previo) => ({ ...previo, nombre_completo: event.target.value }))}
              maxLength={MAX_NOMBRE}
            />
            <SelectorRol
              id={`rol-${cuenta.id}`}
              label={`Rol de ${cuenta.correo}`}
              value={edicion.rol}
              onChange={(event) => setEdicion((previo) => ({ ...previo, rol: event.target.value }))}
            />
            <Button type="submit" loading={ocupado}>
              Guardar
            </Button>
            <Button variant="secondary" onClick={() => setModo('ver')} disabled={ocupado}>
              Cancelar
            </Button>
          </form>
        </td>
      </tr>
    );
  }

  const accionEstado = cuenta.activo
    ? {
        etiqueta: 'Desactivar',
        ejecutar: () => usuariosService.desactivar(cuenta.id),
        aviso: `Cuenta de ${cuenta.nombre_completo} desactivada; sus sesiones abiertas se cerraron.`,
      }
    : {
        etiqueta: 'Reactivar',
        ejecutar: () => usuariosService.reactivar(cuenta.id),
        aviso: `Cuenta de ${cuenta.nombre_completo} reactivada.`,
      };

  return (
    <tr>
      <td className="px-4 py-3">
        {cuenta.nombre_completo}
        {esPropia && <span className="ml-2 text-xs text-gray-600">(tu cuenta)</span>}
      </td>
      <td className="px-4 py-3 break-all">{cuenta.correo}</td>
      <td className="px-4 py-3">{ROLES[cuenta.rol] ?? cuenta.rol}</td>
      <td className="px-4 py-3">
        {cuenta.activo ? (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-900">Activa</span>
        ) : (
          <span className="rounded-full bg-gray-200 px-2 py-0.5 text-gray-800">Desactivada</span>
        )}
        {cuenta.debe_cambiar_password && (
          <span className="mt-1 block text-xs text-amber-800">Contraseña temporal</span>
        )}
      </td>
      <td className="px-4 py-3 whitespace-nowrap">{fechaLegible(cuenta.creado_en)}</td>
      <td className="px-4 py-3">
        {modo === 'confirmar' ? (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm">¿{accionEstado.etiqueta}?</span>
            <Button
              onClick={() => operar(accionEstado.ejecutar, accionEstado.aviso)}
              loading={ocupado}
              aria-label={`Confirmar: ${accionEstado.etiqueta.toLowerCase()} ${cuenta.correo}`}
            >
              Confirmar
            </Button>
            <Button variant="secondary" onClick={() => setModo('ver')} disabled={ocupado}>
              Cancelar
            </Button>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => setModo('editar')} aria-label={`Editar ${cuenta.correo}`}>
              Editar
            </Button>
            <Button
              variant="secondary"
              onClick={() => setModo('confirmar')}
              aria-label={`${accionEstado.etiqueta} ${cuenta.correo}`}
            >
              {accionEstado.etiqueta}
            </Button>
          </div>
        )}
      </td>
    </tr>
  );
}

export default function UsuariosPage() {
  const { usuario } = useAuth();
  const [estado, setEstado] = useState('');
  const [aviso, setAviso] = useState(null);
  const [errorOperacion, setErrorOperacion] = useState(null);
  const esCoordinacion = usuario?.rol === 'coordinacion';

  const { datos, error, cargando, recargar } = useApiQuery(
    ({ signal }) =>
      esCoordinacion
        ? usuariosService.listar({ activo: estado === '' ? undefined : estado === 'true', signal })
        : Promise.resolve([]),
    [estado, esCoordinacion],
  );

  if (!esCoordinacion) {
    return (
      <ErrorAlert
        titulo="Sección exclusiva de Coordinación"
        mensaje="Tu rol no puede gestionar cuentas. Si necesitas una cuenta nueva, pídela a Coordinación."
      />
    );
  }

  /** Ejecuta una operación de escritura y refleja su resultado; devuelve true si tuvo éxito. */
  async function operar(accion, descripcion) {
    setAviso(null);
    setErrorOperacion(null);
    try {
      await accion();
      setAviso(descripcion);
      recargar();
      return true;
    } catch (fallo) {
      setErrorOperacion(fallo.message);
      return false;
    }
  }

  function cuentaCreada(creada) {
    setErrorOperacion(null);
    setAviso(`Cuenta creada para ${creada.nombre_completo} (${ROLES[creada.rol]}). Deberá cambiar su contraseña temporal al ingresar.`);
    recargar();
  }

  const cuentas = datos ?? [];

  return (
    <>
      <h1 className="mb-2 text-3xl font-bold text-green-800">Gestión de usuarios</h1>
      <p className="mb-6 text-gray-600">
        Crea cuentas de Analista SIG o de Coordinación, edita su nombre y rol, y desactívalas cuando ya no deban
        ingresar. Las cuentas no se eliminan para conservar la autoría del historial de las zonas.
      </p>

      <FormularioNuevaCuenta onCreada={cuentaCreada} />

      <div className="mb-4 flex flex-col gap-3" aria-live="polite">
        {aviso && (
          <p role="status" className="rounded-md border border-green-300 bg-green-50 p-4 text-green-900">
            {aviso}
          </p>
        )}
        <ErrorAlert titulo="No se pudo completar la operación" mensaje={errorOperacion} />
      </div>

      <section aria-labelledby="titulo-cuentas" aria-busy={cargando}>
        <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
          <h2 id="titulo-cuentas" className="text-xl font-semibold text-gray-800">
            Cuentas
          </h2>
          <div className="flex flex-col gap-1">
            <label htmlFor="filtro-estado" className="text-sm font-medium text-gray-700">
              Estado
            </label>
            <select
              id="filtro-estado"
              value={estado}
              onChange={(event) => setEstado(event.target.value)}
              className={CLASES_SELECT}
            >
              {OPCIONES_ESTADO.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.etiqueta}
                </option>
              ))}
            </select>
          </div>
        </div>

        {cargando && !datos && <LoadingState mensaje="Cargando cuentas…" />}

        {!cargando && error && (
          <ErrorAlert titulo="No se pudieron cargar las cuentas" mensaje={error.message} onReintentar={recargar} />
        )}

        {!error && datos && cuentas.length === 0 && (
          <p className="rounded-md border border-gray-200 bg-white p-6 text-center text-gray-700">
            No hay cuentas con ese estado.
          </p>
        )}

        {!error && cuentas.length > 0 && (
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
              <caption className="sr-only">Cuentas del sistema</caption>
              <thead className="bg-gray-50 text-gray-700">
                <tr>
                  <th scope="col" className="px-4 py-3 font-semibold">Nombre</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Correo</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Rol</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Estado</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Creada</th>
                  <th scope="col" className="px-4 py-3 font-semibold">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-gray-800">
                {cuentas.map((cuenta) => (
                  <FilaUsuario
                    key={`${cuenta.id}-${cuenta.nombre_completo}-${cuenta.rol}-${cuenta.activo}`}
                    cuenta={cuenta}
                    esPropia={cuenta.id === usuario.id}
                    onOperar={operar}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
