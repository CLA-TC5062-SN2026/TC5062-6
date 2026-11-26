// Mapa temático de las zonas de cambio (RF-06): huella real de cada zona (GeoJSON en EPSG:4326 de la API),
// un círculo proporcional a su superficie alertada, las alertas como puntos, cuadrícula en grados, escala y norte.
// Se dibuja en SVG sin teselas de terceros: no hay peticiones fuera de la propia API.

import { useNavigate } from 'react-router-dom';

const ANCHO = 1000;
const RELACION_MAXIMA = 2.6; // ancho/alto máximo: extensiones muy planas se completan en latitud
const RADIO_MAXIMO = 46; // en unidades del viewBox, para la zona con más superficie alertada
const METROS_POR_GRADO = 111_320;

const formatoArea = new Intl.NumberFormat('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function posiciones(geometria) {
  if (!geometria) return [];
  switch (geometria.type) {
    case 'Point':
      return [geometria.coordinates];
    case 'Polygon':
      return geometria.coordinates.flat();
    case 'MultiPolygon':
      return geometria.coordinates.flat(2);
    default:
      return [];
  }
}

/**
 * Proyección equirectangular local: a la escala de una reserva (decenas de km) la distorsión es despreciable.
 * Devuelve la función de proyección, el alto del viewBox y los límites usados (con margen).
 */
export function crearProyeccion(features) {
  const todas = features.flatMap((f) => posiciones(f.geometry));
  if (todas.length === 0) return null;
  let [oeste, sur, este, norte] = [Infinity, Infinity, -Infinity, -Infinity];
  for (const [lon, lat] of todas) {
    oeste = Math.min(oeste, lon);
    este = Math.max(este, lon);
    sur = Math.min(sur, lat);
    norte = Math.max(norte, lat);
  }
  const latMedia = (sur + norte) / 2;
  const coseno = Math.cos((latMedia * Math.PI) / 180);
  const margen = Math.max(este - oeste, (norte - sur) / coseno, 0.01) * 0.12;
  oeste -= margen;
  este += margen;
  sur -= margen * coseno;
  norte += margen * coseno;
  // Completar en latitud si la extensión es demasiado plana para leerse.
  const altoMinimo = (este - oeste) * coseno / RELACION_MAXIMA;
  if (norte - sur < altoMinimo) {
    const extra = (altoMinimo - (norte - sur)) / 2;
    sur -= extra;
    norte += extra;
  }
  const escala = ANCHO / ((este - oeste) * coseno);
  const alto = (norte - sur) * escala;
  const proyectar = ([lon, lat]) => [(lon - oeste) * coseno * escala, (norte - lat) * escala];
  const metrosPorUnidad = METROS_POR_GRADO / escala;
  return { proyectar, alto, limites: { oeste, sur, este, norte }, metrosPorUnidad };
}

function ruta(geometria, proyectar) {
  const anillos = geometria.type === 'Polygon' ? geometria.coordinates : geometria.coordinates.flat();
  return anillos
    .map((anillo) => anillo.map((p, i) => `${i ? 'L' : 'M'}${proyectar(p).map((v) => v.toFixed(1)).join(' ')}`).join('') + 'Z')
    .join('');
}

function centro(geometria, proyectar) {
  const puntos = posiciones(geometria).map(proyectar);
  const xs = puntos.map(([x]) => x);
  const ys = puntos.map(([, y]) => y);
  return [(Math.min(...xs) + Math.max(...xs)) / 2, (Math.min(...ys) + Math.max(...ys)) / 2];
}

/** Paso "redondo" (1, 2 o 5 × 10^n) cercano al valor pedido. */
function pasoRedondo(valor) {
  const base = 10 ** Math.floor(Math.log10(valor));
  return [1, 2, 5, 10].map((m) => m * base).find((p) => p >= valor) ?? 10 * base;
}

function grados(valor, positivo, negativo) {
  return `${Math.abs(valor).toFixed(2)}° ${valor >= 0 ? positivo : negativo}`;
}

export default function MapaZonas({ zonas, alertas, superficiePorZona }) {
  const navigate = useNavigate();
  const proyeccion = crearProyeccion([...zonas, ...alertas]);
  if (!proyeccion) return null;
  const { proyectar, alto, limites, metrosPorUnidad } = proyeccion;

  const mayor = Math.max(...zonas.map((z) => superficiePorZona[z.properties.codigo] ?? 0), 0.01);
  const simbolos = zonas.map((zona) => {
    const codigo = zona.properties.codigo;
    const superficie = superficiePorZona[codigo] ?? 0;
    const [cx, cy] = centro(zona.geometry, proyectar);
    const r = Math.max(6, RADIO_MAXIMO * Math.sqrt(superficie / mayor));
    const aLaIzquierda = cx + r + 160 > ANCHO;
    return { codigo, superficie, cx, cy, r, aLaIzquierda, d: ruta(zona.geometry, proyectar) };
  });

  const pasoGrados = pasoRedondo((limites.este - limites.oeste) / 6);
  const meridianos = [];
  for (let lon = Math.ceil(limites.oeste / pasoGrados) * pasoGrados; lon < limites.este; lon += pasoGrados) meridianos.push(lon);
  const paralelos = [];
  for (let lat = Math.ceil(limites.sur / pasoGrados) * pasoGrados; lat < limites.norte; lat += pasoGrados) paralelos.push(lat);

  const kmEscala = pasoRedondo((ANCHO * 0.16 * metrosPorUnidad) / 1000);
  const largoEscala = (kmEscala * 1000) / metrosPorUnidad;

  function irAZona(evento, codigo) {
    evento.preventDefault();
    navigate(`/alertas?zona=${encodeURIComponent(codigo)}`);
  }

  return (
    <svg
      viewBox={`0 0 ${ANCHO} ${alto.toFixed(0)}`}
      className="block h-auto w-full"
      role="group"
      aria-label="Mapa de las zonas de cambio. Cada zona enlaza a sus alertas."
    >
      <g stroke="var(--color-linea-tenue)" strokeWidth="1" vectorEffect="non-scaling-stroke">
        {meridianos.map((lon) => {
          const [x] = proyectar([lon, limites.norte]);
          return <line key={`m${lon}`} x1={x} y1="0" x2={x} y2={alto} />;
        })}
        {paralelos.map((lat) => {
          const [, y] = proyectar([limites.oeste, lat]);
          return <line key={`p${lat}`} x1="0" y1={y} x2={ANCHO} y2={y} />;
        })}
      </g>
      <g fontSize="13" fill="var(--color-tinta-suave)" style={{ fontStretch: '80%' }} aria-hidden="true">
        {meridianos.map((lon) => (
          <text key={`tm${lon}`} x={proyectar([lon, limites.sur])[0] + 4} y={alto - 8}>
            {grados(lon, 'E', 'O')}
          </text>
        ))}
        {paralelos.map((lat) => (
          <text key={`tp${lat}`} x="6" y={proyectar([limites.oeste, lat])[1] - 5}>
            {grados(lat, 'N', 'S')}
          </text>
        ))}
      </g>

      {simbolos.map((s) => (
        <circle key={`c${s.codigo}`} cx={s.cx} cy={s.cy} r={s.r} fill="var(--color-perdida)" fillOpacity="0.14"
          stroke="var(--color-perdida)" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
      ))}
      <g fill="none" stroke="var(--color-tinta)" strokeWidth="1.5" vectorEffect="non-scaling-stroke">
        {simbolos.map((s) => <path key={`z${s.codigo}`} d={s.d} />)}
      </g>
      <g aria-hidden="true">
        {alertas.map((alerta) => {
          const [x, y] = proyectar(alerta.geometry.coordinates);
          return alerta.properties.presente_en_ultima_carga === false ? (
            <circle key={alerta.id} cx={x} cy={y} r="2.6" fill="white" stroke="var(--color-tinta-suave)" strokeWidth="1.2" />
          ) : (
            <circle key={alerta.id} cx={x} cy={y} r="2.6" fill="var(--color-perdida)" />
          );
        })}
      </g>

      {simbolos.map((s) => {
        const x = s.aLaIzquierda ? s.cx - s.r - 8 : s.cx + s.r + 8;
        const ancla = s.aLaIzquierda ? 'end' : 'start';
        return (
          <a
            key={`l${s.codigo}`}
            href={`/alertas?zona=${encodeURIComponent(s.codigo)}`}
            onClick={(evento) => irAZona(evento, s.codigo)}
            aria-label={`${s.codigo}: ${formatoArea.format(s.superficie)} ha alertadas. Ver sus alertas`}
            className="group cursor-pointer"
          >
            {/* Área de clic continua: círculo + etiqueta, sin hueco entre ambos. */}
            <circle cx={s.cx} cy={s.cy} r={Math.max(s.r, 14)} fill="transparent" />
            <rect
              x={s.aLaIzquierda ? x - 120 : s.cx}
              y={s.cy - 22}
              width={Math.abs(x - s.cx) + 120}
              height="46"
              fill="transparent"
            />
            <text x={x} y={s.cy - 3} textAnchor={ancla} fontSize="15" fontWeight="650" fill="var(--color-tinta)"
              className="group-hover:underline group-focus:underline" style={{ fontStretch: '90%' }}>
              {s.codigo}
            </text>
            <text x={x} y={s.cy + 15} textAnchor={ancla} fontSize="14" fill="var(--color-tinta-suave)">
              {formatoArea.format(s.superficie)} ha
            </text>
          </a>
        );
      })}

      <g transform={`translate(${ANCHO - 28} 30)`} aria-hidden="true">
        <path d="M0 -14 L8 10 L0 5 L-8 10 Z" fill="var(--color-tinta)" />
        <text x="0" y="28" fontSize="14" fontWeight="650" textAnchor="middle" fill="var(--color-tinta)">N</text>
      </g>
      <g transform={`translate(${ANCHO - 24 - largoEscala} ${alto - 34})`} aria-hidden="true" fontSize="13"
        fill="var(--color-tinta)" style={{ fontStretch: '80%' }}>
        <rect x="0" y="0" width={largoEscala / 2} height="6" fill="var(--color-tinta)" />
        <rect x={largoEscala / 2} y="0" width={largoEscala / 2} height="6" fill="white" stroke="var(--color-tinta)" strokeWidth="1" />
        <text x="0" y="-6" textAnchor="middle">0</text>
        <text x={largoEscala} y="-6" textAnchor="middle">{kmEscala} km</text>
      </g>
    </svg>
  );
}
