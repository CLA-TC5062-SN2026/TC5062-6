// Flujo de negocio: consulta de alertas ingeridas (GET /alertas, RF-04).
// Estados visibles: cargando, error con reintento, sin resultados y resultados paginados.

import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Button from '../components/Button.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import LoadingState from '../components/LoadingState.jsx';
import Segmento from '../components/Segmento.jsx';
import { Aro, PuntoRelleno } from '../components/Simbolo.jsx';
import { useApiQuery } from '../hooks/useApiQuery.js';
import { alertasService } from '../services/alertasService.js';

const TAMANO_PAGINA = 10;
const CODIGO_ZONA = /^EA-\d{4}-\d{3}$/; // components/schemas/CodigoZona del contrato
const OPCIONES_PRESENCIA = [
  { valor: '', etiqueta: 'Todas' },
  { valor: 'true', etiqueta: 'Presentes' },
  { valor: 'false', etiqueta: 'Ausentes' },
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

/** Zona recibida en la URL (p. ej. desde el panel): solo se acepta si cumple el formato del contrato. */
function zonaInicial(params) {
  const zona = (params.get('zona') ?? '').trim().toUpperCase();
  return CODIGO_ZONA.test(zona) ? zona : '';
}

export default function AlertasPage() {
  const [params] = useSearchParams();
  const [zonaEscrita, setZonaEscrita] = useState(() => zonaInicial(params));
  const [errorZona, setErrorZona] = useState('');
  const [filtros, setFiltros] = useState(() => ({ zona: zonaInicial(params), presencia: '' }));
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

  function cambiarPresencia(presencia) {
    setPagina(0);
    setFiltros((previo) => ({ ...previo, presencia }));
  }

  function filtrarPorZona(zona) {
    setZonaEscrita(zona);
    setErrorZona('');
    setPagina(0);
    setFiltros((previo) => ({ ...previo, zona }));
  }

  const total = datos?.total ?? 0;
  const totalPaginas = Math.max(1, Math.ceil(total / TAMANO_PAGINA));
  const alertas = datos?.alertas ?? [];

  const desde = pagina * TAMANO_PAGINA + 1;
  const hasta = pagina * TAMANO_PAGINA + alertas.length;

  return (
    <>
      <div className="flex flex-wrap items-baseline gap-x-5 gap-y-1">
        <h1 className="ancho-titulo text-4xl leading-tight font-bold">Alertas de deforestación</h1>
        {!cargando && !error && (
          <p className="text-[17px] text-tinta-suave tabular-nums" aria-live="polite">
            {total} {total === 1 ? 'alerta encontrada' : 'alertas encontradas'}
          </p>
        )}
      </div>

      <div className="flex flex-wrap items-end gap-x-5 gap-y-3">
        <form onSubmit={aplicarFiltros} className="flex items-end gap-2" role="search" aria-label="Filtrar por zona">
          <div className="w-56">
            <Input
              label="Código de zona"
              name="zona"
              value={zonaEscrita}
              onChange={(event) => setZonaEscrita(event.target.value)}
              placeholder="p. ej. EA-2026-101"
              error={errorZona}
              autoComplete="off"
            />
          </div>
          <Button type="submit" variant="secondary" className={errorZona ? 'mb-7' : ''}>
            Buscar
          </Button>
        </form>
        <div className="flex flex-col gap-1.5">
          <span id="etiqueta-presencia" className="text-sm font-semibold">
            En la última carga
          </span>
          <Segmento
            etiquetaId="etiqueta-presencia"
            opciones={OPCIONES_PRESENCIA}
            valor={filtros.presencia}
            onCambiar={cambiarPresencia}
          />
        </div>
        {filtros.zona && (
          <Button variant="texto" onClick={() => filtrarPorZona('')}>
            Ver todas las zonas
          </Button>
        )}
      </div>

      <section aria-labelledby="titulo-resultados" aria-busy={cargando} className="flex flex-col gap-3">
        <h2 id="titulo-resultados" className="sr-only">
          Resultados
        </h2>

        {cargando && <LoadingState mensaje="Cargando alertas desde el servidor…" />}

        {!cargando && error && (
          <ErrorAlert titulo="No se pudieron cargar las alertas" mensaje={error.message} onReintentar={recargar} />
        )}

        {!cargando && !error && alertas.length === 0 && (
          <p className="rounded-md border border-linea bg-white p-6 text-center text-tinta-suave">
            No hay alertas que coincidan con los filtros.
          </p>
        )}

        {!cargando && !error && alertas.length > 0 && (
          <>
            <div className="overflow-x-auto rounded-md border border-linea bg-white">
              <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
                <caption className="sr-only">Alertas de deforestación, página {pagina + 1}</caption>
                <thead className="ancho-encabezado text-[13px] text-tinta-suave">
                  <tr className="border-b-2 border-tinta">
                    <th scope="col" className="px-5 py-3 font-semibold">Alerta</th>
                    <th scope="col" className="px-3 py-3 font-semibold">Zona</th>
                    <th scope="col" className="px-3 py-3 font-semibold">Detectada</th>
                    <th scope="col" className="px-3 py-3 text-right font-semibold">Área (ha)</th>
                    <th scope="col" className="px-5 py-3 font-semibold">En la última carga</th>
                  </tr>
                </thead>
                <tbody>
                  {alertas.map((alerta) => (
                    <tr key={alerta.id} className="border-t border-linea-tenue">
                      <td className="ancho-codigo h-12 px-5 font-semibold whitespace-nowrap">{alerta.codigo}</td>
                      <td className="px-3">
                        <button
                          type="button"
                          onClick={() => filtrarPorZona(alerta.zona_codigo)}
                          title={`Ver solo la zona ${alerta.zona_codigo}`}
                          className="ancho-codigo -ml-1.5 min-h-9 whitespace-nowrap rounded px-1.5 text-dosel underline decoration-linea-fuerte underline-offset-4 hover:decoration-dosel"
                        >
                          {alerta.zona_codigo}
                        </button>
                      </td>
                      <td className="px-3 whitespace-nowrap text-tinta-suave">{fechaLegible(alerta.fecha_deteccion)}</td>
                      <td className="px-3 text-right tabular-nums">{formatoArea.format(alerta.area_ha)}</td>
                      <td className="px-5">
                        {alerta.presente_en_ultima_carga ? (
                          <span className="inline-flex items-center gap-2">
                            <PuntoRelleno />
                            Presente
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-2 text-tinta-suave">
                            <Aro />
                            Ausente
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <nav aria-label="Paginación de alertas" className="flex flex-wrap items-center justify-between gap-3">
              <span className="text-sm text-tinta-suave tabular-nums">
                {desde}–{hasta} de {total}
              </span>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => setPagina((p) => p - 1)} disabled={pagina === 0}>
                  Anterior
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setPagina((p) => p + 1)}
                  disabled={pagina + 1 >= totalPaginas}
                >
                  Siguiente
                </Button>
              </div>
            </nav>
          </>
        )}
      </section>
    </>
  );
}
