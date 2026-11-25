// Simbología de estado compartida con el mapa: punto relleno = presente/activa, aro = ausente/desactivada.
// El texto siempre acompaña al símbolo, así el estado no depende solo del color (WCAG 1.4.1).

const COLORES = {
  perdida: 'var(--color-perdida)',
  dosel: 'var(--color-dosel)',
};

export function PuntoRelleno({ color = 'perdida' }) {
  return (
    <svg aria-hidden="true" width="12" height="12" className="shrink-0">
      <circle cx="6" cy="6" r="5" fill={COLORES[color]} />
    </svg>
  );
}

export function Aro() {
  return (
    <svg aria-hidden="true" width="12" height="12" className="shrink-0">
      <circle cx="6" cy="6" r="4.5" fill="none" stroke="var(--color-tinta-suave)" strokeWidth="1.5" />
    </svg>
  );
}
