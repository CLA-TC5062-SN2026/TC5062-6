// Flujo de negocio: consulta de alertas ingeridas (GET /alertas, RF-04).
// Estados visibles: cargando, error con reintento, sin resultados y resultados paginados.

import { useState } from 'react';
import Button from '../components/Button.jsx';
import Card from '../components/Card.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import LoadingState from '../components/LoadingState.jsx';
import { useApiQuery } from '../hooks/useApiQuery.js';
import { alertasService } from '../services/alertasService.js';

const TAMANO_PAGINA = 10;
const CODIGO_ZONA = /^EA-\d{4}-\d{3}$/; // components/schemas/CodigoZona del contrato
const OPCIONES_PRESENCIA = [
  { valor: '', etiqueta: 'Todas' },
  { valor: 'true', etiqueta: 'Presentes en la última carga' },
  { valor: 'false', etiqueta: 'Ausentes en la última carga' },
];

const formatoArea = new Intl.NumberFormat('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const formatoFecha = new Intl.DateTimeFormat('es-PE', { dateStyle: 'medium', timeZone: 'UTC' });

/** fecha_deteccion es una fecha sin hora (YYYY-MM-DD): se formatea en UTC para no correr el día. */
function fechaLegible(isoFecha) {
  const fecha = new Date(`${isoFecha}T00:00:00Z`);
  return Number.isNaN(fecha.getTime()) ? isoFecha : formatoFecha.format(fecha);
}

function presenciaComoFiltro(valor) {
  if (valor === '') return undefined;
  return valor === 'true';
}

export default function AlertasPage() {
  const [zonaEscrita, setZonaEscrita] = useState('');
  const [errorZona, setErrorZona] = useState('');
  const [filtros, setFiltros] = useState({ zona: '', presencia: '' });
  const [pagina, setPagina] = useState(0);

  const { datos, error, cargando, recargar } = useApiQuery(
    ({ signal }) =>
      alertasService.listar({
        zona: filtros.zona || undefined,
        presenteEnUltimaCarga: presenciaComoFiltro(filtros.presencia),
        limite: TAMANO_PAGINA,
        desplazamiento: pagina * TAMANO_PAGINA,
        signal,
      }),
    [filtros.zona, filtros.presencia, pagina],
  );

  function aplicarFiltros(event) {
    event.preventDefault();
    const zona = zonaEscrita.trim().toUpperCase();
    // Validación en el cliente con la misma regla del contrato: evita un 400 evitable.
    if (zona && !CODIGO_ZONA.test(zona)) {
      setErrorZona('Usa el formato EA-AAAA-NNN, por ejemplo EA-2026-001.');
      return;
    }
    setErrorZona('');
    setPagina(0);
    setFiltros((previo) => ({ ...previo, zona }));
  }

  function cambiarPresencia(event) {
    setPagina(0);
    setFiltros((previo) => ({ ...previo, presencia: event.target.value }));
  }

  const total = datos?.total ?? 0;
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_PAGINA));
  const alertas = datos?.alertas ?? [];

  return (
    <>
      <h1 className="mb-2 text-3xl font-bold text-green-800">Alertas de deforestación</h1>
      <p className="mb-6 text-gray-600">
        Alertas de GeoBosques ingeridas por EcoAlert, ordenadas de la más reciente a la más antigua.
      </p>

      <Card title="Filtros" headingLevel={2} className="mb-6">
        <form onSubmit={aplicarFiltros} className="grid grid-cols-1 items-end gap-4 md:grid-cols-[1fr_1fr_auto]">
          <Input
            label="Código de zona"
            name="zona"
            value={zonaEscrita}
            onChange={(event) => setZonaEscrita(event.target.value)}
            placeholder="EA-2026-001"
            error={errorZona}
            autoComplete="off"
          />
          <div className="flex flex-col gap-1">
            <label htmlFor="filtro-presencia" className="text-sm font-medium text-gray-700">
              Presencia en la última carga
            </label>
            <select
              id="filtro-presencia"
              value={filtros.presencia}
              onChange={cambiarPresencia}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-700"
            >
              {OPCIONES_PRESENCIA.map((opcion) => (
                <option key={opcion.valor} value={opcion.valor}>
                  {opcion.etiqueta}
                </option>
              ))}
            </select>
          </div>
          <Button type="submit">Buscar</Button>
        </form>
      </Card>

      <section aria-labelledby="titulo-resultados" aria-busy={cargando}>
        <h2 id="titulo-resultados" className="sr-only">
          Resultados
        </h2>

        {cargando && <LoadingState mensaje="Cargando alertas desde el servidor…" />}

        {!cargando && error && (
          <ErrorAlert titulo="No se pudieron cargar las alertas" mensaje={error.message} onReintentar={recargar} />
        )}

        {!cargando && !error && alertas.length === 0 && (
          <p className="rounded-md border border-gray-200 bg-white p-6 text-center text-gray-700">
            No hay alertas que coincidan con los filtros.
          </p>
        )}

        {!cargando && !error && alertas.length > 0 && (
          <>
            <p className="mb-3 text-sm text-gray-700" aria-live="polite">
              {total} {total === 1 ? 'alerta encontrada' : 'alertas encontradas'}
            </p>
            <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
              <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
                <caption className="sr-only">Alertas de deforestación, página {pagina + 1}</caption>
                <thead className="bg-gray-50 text-gray-700">
                  <tr>
                    <th scope="col" className="px-4 py-3 font-semibold">Código</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Fuente</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Zona</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Detectada</th>
                    <th scope="col" className="px-4 py-3 text-right font-semibold">Área (ha)</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Última carga</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-gray-800">
                  {alertas.map((alerta) => (
                    <tr key={alerta.id}>
                      <td className="px-4 py-3 font-mono">{alerta.codigo}</td>
                      <td className="px-4 py-3">{alerta.fuente}</td>
                      <td className="px-4 py-3 font-mono">{alerta.zona_codigo}</td>
                      <td className="px-4 py-3">{fechaLegible(alerta.fecha_deteccion)}</td>
                      <td className="px-4 py-3 text-right tabular-nums">{formatoArea.format(alerta.area_ha)}</td>
                      <td className="px-4 py-3">
                        {alerta.presente_en_ultima_carga ? (
                          <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-900">Presente</span>
                        ) : (
                          <span className="rounded-full bg-gray-200 px-2 py-0.5 text-gray-800">Ausente</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <nav aria-label="Paginación de alertas" className="mt-4 flex items-center justify-between gap-3">
              <Button variant="secondary" onClick={() => setPagina((p) => p - 1)} disabled={pagina === 0}>
                Anterior
              </Button>
              <span className="text-sm text-gray-700">
                Página {pagina + 1} de {totalPaginas}
              </span>
              <Button
                variant="secondary"
                onClick={() => setPagina((p) => p + 1)}
                disabled={pagina + 1 >= totalPaginas}
              >
                Siguiente
              </Button>
            </nav>
          </>
        )}
      </section>
    </>
  );
}
