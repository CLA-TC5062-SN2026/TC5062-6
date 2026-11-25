// Flujo de negocio: gestión de cuentas por Coordinación (RF-02). CRUD sobre /usuarios:
// crear (POST, idempotente), leer (GET), actualizar (PATCH merge-patch) y baja lógica (desactivar/reactivar).
// Las cuentas no se eliminan (RF-02-AC-7): conservar la cuenta conserva la autoría del historial de zonas.
// La autorización real la aplica el backend (403 para Analista SIG, RNF-02); aquí solo se evita mostrar
// una pantalla que no puede usar.

import { useId, useRef, useState } from 'react';
import Button from '../components/Button.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import LoadingState from '../components/LoadingState.jsx';
import Segmento from '../components/Segmento.jsx';
import { Aro, PuntoRelleno } from '../components/Simbolo.jsx';
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
const CLASES_SELECT = 'h-11 rounded border border-linea-fuerte bg-white px-3 text-tinta';
// Coordinación en azul río y Analista SIG en verde dosel, igual que en la barra superior.
const COLOR_ROL = { coordinacion: 'text-rio', analista_sig: 'text-dosel' };

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
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-semibold">
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

/** Rol de la cuenta nueva como opciones visibles: son solo dos y así se ven ambas sin abrir un menú. */
function OpcionesRol({ value, onChange }) {
  return (
    <fieldset className="flex flex-col gap-1">
      <legend className="mb-1.5 text-sm font-semibold">Rol</legend>
      {Object.entries(ROLES).map(([valor, etiqueta]) => (
        <label key={valor} className="flex min-h-9 cursor-pointer items-center gap-2.5">
          <input
            type="radio"
            name="rol_nueva_cuenta"
            value={valor}
            checked={value === valor}
            onChange={onChange}
            className="h-[18px] w-[18px] accent-dosel"
          />
          {etiqueta}
        </label>
      ))}
    </fieldset>
  );
}

function FormularioNuevaCuenta({ id, onCreada, onCerrar }) {
  const tituloId = useId();
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
    <section
      id={id}
      aria-labelledby={tituloId}
      className="flex-[1_1_300px] rounded-md border border-tinta bg-white p-5 sm:p-6"
    >
      <div className="mb-4 flex items-center justify-between gap-2">
        <h2 id={tituloId} className="ancho-seccion text-xl font-bold">
          Nueva cuenta
        </h2>
        <button
          type="button"
          onClick={onCerrar}
          aria-label="Cerrar el formulario de nueva cuenta"
          className="flex h-10 w-10 items-center justify-center rounded text-tinta-suave hover:bg-papel hover:text-tinta"
        >
          <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M6 6l12 12" />
            <path d="M18 6L6 18" />
          </svg>
        </button>
      </div>
      <form noValidate onSubmit={enviar} className="flex flex-col gap-4">
        <ErrorAlert titulo="No se pudo crear la cuenta" mensaje={errorServidor} />
        <Input
          label="Nombre completo"
          name="nombre_completo"
          value={form.nombreCompleto}
          onChange={actualizar('nombreCompleto')}
          error={errores.nombreCompleto}
          maxLength={MAX_NOMBRE}
          autoComplete="off"
          autoFocus
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
        <OpcionesRol value={form.rol} onChange={actualizar('rol')} />
        <div className="flex flex-col gap-1.5">
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
          {!errores.passwordTemporal && (
            <p className="text-sm text-tinta-suave">Al menos {MIN_PASSWORD} caracteres. Se cambia en el primer ingreso.</p>
          )}
        </div>
        <Button type="submit" loading={enviando}>
          Crear cuenta
        </Button>
      </form>
    </section>
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
      <tr className="border-t border-linea-tenue">
        <td colSpan={4} className="bg-dosel-tenue px-5 py-4">
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
        consecuencia: `${cuenta.nombre_completo} no podrá ingresar y sus sesiones abiertas se cerrarán.`,
        ejecutar: () => usuariosService.desactivar(cuenta.id),
        aviso: `Cuenta de ${cuenta.nombre_completo} desactivada; sus sesiones abiertas se cerraron.`,
      }
    : {
        etiqueta: 'Reactivar',
        consecuencia: `${cuenta.nombre_completo} podrá volver a ingresar con su contraseña actual.`,
        ejecutar: () => usuariosService.reactivar(cuenta.id),
        aviso: `Cuenta de ${cuenta.nombre_completo} reactivada.`,
      };
  const destructiva = cuenta.activo;

  return (
    <>
      <tr className="border-t border-linea-tenue">
        <td className="px-5 py-3">
          <span className={`block font-semibold ${cuenta.activo ? '' : 'text-tinta-suave'}`}>
            {cuenta.nombre_completo}
            {esPropia && <span className="ml-1.5 font-normal text-tinta-suave">(tu cuenta)</span>}
          </span>
          <span className="block text-[13px] text-tinta-suave">{cuenta.correo}</span>
        </td>
        <td className={`px-3 py-3 font-semibold whitespace-nowrap ${COLOR_ROL[cuenta.rol] ?? ''}`}>{ROLES[cuenta.rol] ?? cuenta.rol}</td>
        <td className="px-3 py-3">
          {cuenta.activo ? (
            <span className="inline-flex items-center gap-2">
              <PuntoRelleno color="dosel" />
              Activa
            </span>
          ) : (
            <span className="inline-flex items-center gap-2 text-tinta-suave">
              <Aro />
              Desactivada
            </span>
          )}
          {cuenta.debe_cambiar_password && <span className="block text-[13px] text-ocre-texto">Contraseña temporal</span>}
        </td>
        <td className="px-5 py-3">
          <div className="flex justify-end gap-1">
            <Button
              variant="texto"
              onClick={() => setModo('editar')}
              aria-label={`Editar ${cuenta.correo}`}
              className="min-h-10 text-sm"
            >
              Editar
            </Button>
            <Button
              variant="texto"
              onClick={() => setModo('confirmar')}
              aria-label={`${accionEstado.etiqueta} ${cuenta.correo}`}
              aria-expanded={modo === 'confirmar'}
              className={`min-h-10 text-sm ${destructiva ? 'text-peligro hover:bg-peligro-tenue' : ''}`}
            >
              {accionEstado.etiqueta}
            </Button>
          </div>
        </td>
      </tr>
      {modo === 'confirmar' && (
        <tr>
          <td colSpan={4} className="px-5 pb-4">
            <div
              className={`flex flex-wrap items-center justify-between gap-3 border-l-4 px-4 py-3 ${
                destructiva ? 'border-peligro bg-peligro-tenue text-peligro-texto' : 'border-dosel bg-dosel-tenue'
              }`}
            >
              <p>{accionEstado.consecuencia}</p>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => setModo('ver')} disabled={ocupado} className="min-h-10 text-sm">
                  Cancelar
                </Button>
                <Button
                  variant={destructiva ? 'peligro' : 'primary'}
                  onClick={() => operar(accionEstado.ejecutar, accionEstado.aviso)}
                  loading={ocupado}
                  aria-label={`${accionEstado.etiqueta} cuenta de ${cuenta.correo}`}
                  className="min-h-10 text-sm"
                >
                  {accionEstado.etiqueta} cuenta
                </Button>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function UsuariosPage() {
  const { usuario } = useAuth();
  const [estado, setEstado] = useState('');
  const [aviso, setAviso] = useState(null);
  const [errorOperacion, setErrorOperacion] = useState(null);
  const [formularioAbierto, setFormularioAbierto] = useState(false);
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
    setFormularioAbierto(false);
    recargar();
  }

  const cuentas = datos ?? [];

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="ancho-titulo text-4xl leading-tight font-bold">Usuarios</h1>
        <Button
          onClick={() => setFormularioAbierto((abierto) => !abierto)}
          aria-expanded={formularioAbierto}
          aria-controls="formulario-nueva-cuenta"
        >
          Nueva cuenta
        </Button>
      </div>

      <div className="flex flex-col gap-3 empty:hidden" aria-live="polite">
        {aviso && (
          <p role="status" className="border-l-4 border-dosel bg-dosel-tenue px-4 py-3">
            {aviso}
          </p>
        )}
        <ErrorAlert titulo="No se pudo completar la operación" mensaje={errorOperacion} />
      </div>

      <div className="flex flex-wrap items-start gap-6">
        <section aria-labelledby="titulo-cuentas" aria-busy={cargando} className="flex min-w-0 flex-[999_1_600px] flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 id="titulo-cuentas" className="ancho-seccion text-xl font-bold">
              Cuentas
            </h2>
            <Segmento etiqueta="Estado de la cuenta" opciones={OPCIONES_ESTADO} valor={estado} onCambiar={setEstado} />
          </div>

          {cargando && !datos && <LoadingState mensaje="Cargando cuentas…" />}

          {!cargando && error && (
            <ErrorAlert titulo="No se pudieron cargar las cuentas" mensaje={error.message} onReintentar={recargar} />
          )}

          {!error && datos && cuentas.length === 0 && (
            <p className="rounded-md border border-linea bg-white p-6 text-center text-tinta-suave">
              No hay cuentas con ese estado.
            </p>
          )}

          {!error && cuentas.length > 0 && (
            <div className="overflow-x-auto rounded-md border border-linea bg-white">
              <table className="w-full min-w-[38rem] border-collapse text-left text-sm">
                <caption className="sr-only">Cuentas del sistema</caption>
                <thead className="ancho-encabezado text-[13px] text-tinta-suave">
                  <tr className="border-b-2 border-tinta">
                    <th scope="col" className="px-5 py-3 font-semibold">Persona</th>
                    <th scope="col" className="px-3 py-3 font-semibold">Rol</th>
                    <th scope="col" className="px-3 py-3 font-semibold">Estado</th>
                    <th scope="col" className="px-5 py-3">
                      <span className="sr-only">Acciones</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
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

        {formularioAbierto && (
          <FormularioNuevaCuenta
            id="formulario-nueva-cuenta"
            onCreada={cuentaCreada}
            onCerrar={() => setFormularioAbierto(false)}
          />
        )}
      </div>
    </>
  );
}
