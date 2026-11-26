// Panel principal tras iniciar sesión (ruta protegida).
// Las cifras y el resumen por zona se calculan en el cliente con GET /alertas y GET /cargas-alertas:
// el contrato aún no tiene un endpoint de resumen implementado (GET /zonas está especificado, no construido).
// El mapa usa GET /mapa/capas/{capa}/elementos (RF-06): geometría real de PostGIS en EPSG:4326.

import { Link } from 'react-router-dom';
import ErrorAlert from '../components/ErrorAlert.jsx';
import LoadingState from '../components/LoadingState.jsx';
import MapaZonas from '../components/MapaZonas.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { useApiQuery } from '../hooks/useApiQuery.js';
import { LIMITE_MAXIMO, alertasService } from '../services/alertasService.js';
import { mapaService } from '../services/mapaService.js';

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
  const mapa = useApiQuery(
    ({ signal }) =>
      Promise.all([
        mapaService.elementos('zonas_cambio', { signal }),
        mapaService.elementos('alertas_geobosques', { signal }),
      ]),
    [],
  );

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
          <div className="flex flex-wrap items-stretch gap-6">
            <Mapa consulta={mapa} zonas={zonas} />
            <dl className="grid flex-[1_1_240px] grid-cols-2 content-start border-t-2 border-tinta lg:grid-cols-1">
              <Cifra etiqueta="Alertas cargadas" valor={total} />
              <Cifra etiqueta="Zonas de cambio" valor={zonas.length} />
              <Cifra etiqueta="Superficie alertada" valor={formatoArea.format(superficie)} unidad="ha" destacada />
              <Cifra etiqueta="Ausentes en la última carga" valor={ausentes} />
            </dl>
          </div>

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

/** Lámina del mapa con marco de hoja cartográfica; el resto del panel funciona aunque el mapa falle. */
function Mapa({ consulta, zonas }) {
  const [capaZonas, capaAlertas] = Array.isArray(consulta.datos) ? consulta.datos : [];
  const featuresZonas = Array.isArray(capaZonas?.features) ? capaZonas.features : [];
  const featuresAlertas = Array.isArray(capaAlertas?.features)
    ? capaAlertas.features.filter((f) => f.geometry?.type === 'Point')
    : [];
  const superficiePorZona = Object.fromEntries(zonas.map((z) => [z.codigo, z.superficie]));

  return (
    <figure className="m-0 min-w-0 flex-[3_1_620px] border border-tinta bg-white p-1.5">
      <div className="flex h-full flex-col border border-linea-fuerte">
        <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 px-4 pt-3">
          <figcaption className="ancho-seccion font-bold">Zonas de cambio con alertas</figcaption>
          <span className="text-[13px] text-tinta-suave">Pulsa una zona para ver sus alertas</span>
        </div>
        <div className="grow px-2">
          {consulta.cargando && <LoadingState mensaje="Cargando el mapa…" />}
          {!consulta.cargando && consulta.error && (
            <div className="p-3">
              <ErrorAlert titulo="No se pudo cargar el mapa" mensaje={consulta.error.message} onReintentar={consulta.recargar} />
            </div>
          )}
          {!consulta.cargando && !consulta.error && featuresZonas.length === 0 && (
            <p className="p-6 text-tinta-suave">Todavía no hay zonas con geometría para dibujar.</p>
          )}
          {!consulta.cargando && !consulta.error && featuresZonas.length > 0 && (
            // En pantallas angostas el mapa conserva un ancho legible y se desplaza dentro de su marco.
            <div className="overflow-x-auto">
              <div className="min-w-[640px]">
                <MapaZonas zonas={featuresZonas} alertas={featuresAlertas} superficiePorZona={superficiePorZona} />
              </div>
            </div>
          )}
        </div>
        <ul className="flex flex-wrap gap-x-5 gap-y-1 px-4 pb-3 text-[13px] text-tinta-suave">
          <li className="flex items-center gap-2">
            <svg aria-hidden="true" width="14" height="14"><rect x="1" y="1" width="12" height="12" fill="none" stroke="var(--color-tinta)" strokeWidth="1.5" /></svg>
            Zona de cambio
          </li>
          <li className="flex items-center gap-2">
            <svg aria-hidden="true" width="16" height="16"><circle cx="8" cy="8" r="7" fill="var(--color-perdida)" fillOpacity="0.14" stroke="var(--color-perdida)" strokeWidth="1.5" /></svg>
            Superficie alertada (área del círculo)
          </li>
          <li className="flex items-center gap-2">
            <svg aria-hidden="true" width="10" height="10"><circle cx="5" cy="5" r="4" fill="var(--color-perdida)" /></svg>
            Alerta presente
          </li>
          <li className="flex items-center gap-2">
            <svg aria-hidden="true" width="10" height="10"><circle cx="5" cy="5" r="3.5" fill="white" stroke="var(--color-tinta-suave)" strokeWidth="1.2" /></svg>
            Ausente en la última carga
          </li>
        </ul>
      </div>
    </figure>
  );
}

function Cifra({ etiqueta, valor, unidad, destacada = false }) {
  return (
    <div className="flex flex-col gap-0.5 border-b border-linea py-4 pr-4 max-lg:odd:pr-4 max-lg:even:pl-4">
      <dt className="text-sm text-tinta-suave">{etiqueta}</dt>
      <dd className={`ancho-cifra text-4xl leading-none font-bold ${destacada ? 'text-perdida' : ''}`}>
        {valor}
        {unidad && <span className="ml-1 text-lg font-semibold">{unidad}</span>}
      </dd>
    </div>
  );
}
