// Panel principal tras iniciar sesión (ruta protegida).
// Las cifras y el resumen por zona se calculan en el cliente con GET /alertas y GET /cargas-alertas:
// el contrato aún no tiene un endpoint de resumen implementado (GET /zonas está especificado, no construido).

import { Link } from 'react-router-dom';
import ErrorAlert from '../components/ErrorAlert.jsx';
import LoadingState from '../components/LoadingState.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { useApiQuery } from '../hooks/useApiQuery.js';
import { LIMITE_MAXIMO, alertasService } from '../services/alertasService.js';

const formatoArea = new Intl.NumberFormat('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const formatoFecha = new Intl.DateTimeFormat('es-PE', { dateStyle: 'medium', timeZone: 'UTC' });

/** Fechas sin hora (YYYY-MM-DD): se formatean en UTC para no correr el día. */
function fechaLegible(isoFecha) {
  const fecha = new Date(`${isoFecha}T00:00:00Z`);
  return Number.isNaN(fecha.getTime()) ? isoFecha : formatoFecha.format(fecha);
}

/** Agrupa las alertas por zona: número de alertas, superficie alertada y detección más reciente. */
export function resumirAlertas(alertas) {
  const zonas = new Map();
  let ausentes = 0;
  let superficie = 0;
  for (const alerta of alertas) {
    if (!alerta.presente_en_ultima_carga) ausentes += 1;
    superficie += alerta.area_ha;
    const zona = zonas.get(alerta.zona_codigo) ?? {
      codigo: alerta.zona_codigo,
      alertas: 0,
      superficie: 0,
      ultimaDeteccion: alerta.fecha_deteccion,
    };
    zona.alertas += 1;
    zona.superficie += alerta.area_ha;
    if (alerta.fecha_deteccion > zona.ultimaDeteccion) zona.ultimaDeteccion = alerta.fecha_deteccion;
    zonas.set(alerta.zona_codigo, zona);
  }
  return {
    ausentes,
    superficie,
    zonas: [...zonas.values()].sort((a, b) => b.superficie - a.superficie || a.codigo.localeCompare(b.codigo)),
  };
}

export default function DashboardPage() {
  const { usuario } = useAuth();
  const temporal = usuario.debe_cambiar_password;

  return (
    <>
      {temporal && (
        <div
          role="alert"
          className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-ocre/40 bg-ocre-tenue px-5 py-4 text-ocre-texto"
        >
          <p>Tu cuenta tiene una contraseña temporal. Cámbiala para consultar la información del sistema.</p>
          <Link
            to="/cambiar-password"
            className="inline-flex min-h-10 items-center rounded bg-ocre-texto px-4 font-semibold text-white hover:bg-tinta"
          >
            Cambiar mi contraseña
          </Link>
        </div>
      )}

      {/* Mientras la contraseña sea temporal el backend responde 403 a las consultas: no se piden. */}
      {temporal ? <h1 className="ancho-titulo text-4xl leading-tight font-bold">Panel</h1> : <Resumen />}
    </>
  );
}

function Resumen() {
  const alertas = useApiQuery(({ signal }) => alertasService.listar({ limite: LIMITE_MAXIMO, signal }), []);
  const cargas = useApiQuery(({ signal }) => alertasService.listarCargas({ signal }), []);

  const ultimaCarga = Array.isArray(cargas.datos) ? cargas.datos[0] : undefined;
  const lista = Array.isArray(alertas.datos?.alertas) ? alertas.datos.alertas : [];
  const total = alertas.datos?.total ?? lista.length;
  const { ausentes, superficie, zonas } = resumirAlertas(lista);
  const mayor = zonas[0]?.superficie || 1;

  return (
    <>
      <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-2">
        <h1 className="ancho-titulo text-4xl leading-tight font-bold">Panel</h1>
        {ultimaCarga && (
          <p className="text-tinta-suave">
            Última carga de {ultimaCarga.fuente}:{' '}
            <strong className="font-semibold text-tinta">{fechaLegible(ultimaCarga.fecha_corte)}</strong>, por{' '}
            {ultimaCarga.cargada_por?.nombre_completo}
          </p>
        )}
      </div>

      {alertas.cargando && <LoadingState mensaje="Calculando el resumen de alertas…" />}

      {!alertas.cargando && alertas.error && (
        <ErrorAlert titulo="No se pudo cargar el resumen" mensaje={alertas.error.message} onReintentar={alertas.recargar} />
      )}

      {!alertas.cargando && !alertas.error && total === 0 && (
        <p className="rounded-md border border-linea bg-white p-6 text-tinta-suave">
          Todavía no hay alertas cargadas. Cuando se cargue un archivo de GeoBosques, su resumen aparecerá aquí.
        </p>
      )}

      {!alertas.cargando && !alertas.error && total > 0 && (
        <>
          <dl className="grid grid-cols-2 border-t-2 border-tinta md:grid-cols-4">
            <Cifra etiqueta="Alertas cargadas" valor={total} />
            <Cifra etiqueta="Zonas de cambio" valor={zonas.length} />
            <Cifra etiqueta="Superficie alertada" valor={formatoArea.format(superficie)} unidad="ha" destacada />
            <Cifra etiqueta="Ausentes en la última carga" valor={ausentes} />
          </dl>

          {total > lista.length && (
            <p className="text-sm text-tinta-suave">
              El resumen usa las {lista.length} alertas más recientes de {total}.
            </p>
          )}

          <section aria-labelledby="titulo-zonas" className="flex flex-col gap-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="titulo-zonas" className="ancho-seccion text-xl font-bold">
                Zonas por superficie alertada
              </h2>
              <Link to="/alertas" className="font-semibold text-dosel underline-offset-4 hover:underline">
                Ver las {total} alertas
              </Link>
            </div>
            <div className="overflow-x-auto rounded-md border border-linea bg-white">
              <table className="w-full min-w-[36rem] border-collapse text-left text-sm">
                <caption className="sr-only">Zonas de cambio ordenadas por superficie alertada</caption>
                <thead className="ancho-encabezado text-[13px] text-tinta-suave">
                  <tr className="border-b-2 border-tinta">
                    <th scope="col" className="px-5 py-3 font-semibold">Zona</th>
                    <th scope="col" className="px-3 py-3 text-right font-semibold">Alertas</th>
                    <th scope="col" className="min-w-64 px-3 py-3 font-semibold">Superficie alertada (ha)</th>
                    <th scope="col" className="px-5 py-3 font-semibold">Última detección</th>
                  </tr>
                </thead>
                <tbody>
                  {zonas.map((zona) => (
                    <tr key={zona.codigo} className="border-t border-linea-tenue">
                      <td className="h-12 px-5">
                        <Link
                          to={`/alertas?zona=${encodeURIComponent(zona.codigo)}`}
                          className="ancho-codigo font-semibold whitespace-nowrap text-tinta underline decoration-linea-fuerte underline-offset-4 hover:decoration-dosel"
                        >
                          {zona.codigo}
                        </Link>
                      </td>
                      <td className="px-3 text-right tabular-nums">{zona.alertas}</td>
                      <td className="px-3">
                        <div className="flex items-center gap-3">
                          <span className="w-14 text-right tabular-nums">{formatoArea.format(zona.superficie)}</span>
                          <span aria-hidden="true" className="block h-2 grow bg-perdida-tenue">
                            <span
                              className="block h-2 bg-perdida"
                              style={{ width: `${Math.max(2, (zona.superficie / mayor) * 100)}%` }}
                            />
                          </span>
                        </div>
                      </td>
                      <td className="px-5 text-tinta-suave">{fechaLegible(zona.ultimaDeteccion)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}

function Cifra({ etiqueta, valor, unidad, destacada = false }) {
  return (
    <div className="flex flex-col gap-0.5 border-b border-linea py-4 pr-4 md:border-r md:last:border-r-0 md:[&:not(:first-child)]:pl-5">
      <dt className="text-sm text-tinta-suave">{etiqueta}</dt>
      <dd className={`ancho-cifra text-4xl leading-none font-bold ${destacada ? 'text-perdida' : ''}`}>
        {valor}
        {unidad && <span className="ml-1 text-lg font-semibold">{unidad}</span>}
      </dd>
    </div>
  );
}
