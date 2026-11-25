// Marca de EcoAlert: una zona de cambio (cuadro) con una alerta (punto magenta).
// Es el mismo símbolo que usa la interfaz para zonas y alertas.

export default function Marca({ tamano = 26 }) {
  return (
    <svg aria-hidden="true" width={tamano} height={tamano} viewBox="0 0 26 26" className="shrink-0">
      <rect x="2" y="2" width="22" height="22" fill="none" stroke="var(--color-dosel)" strokeWidth="2" />
      <circle cx="16.5" cy="9.5" r="3.5" fill="var(--color-perdida)" />
    </svg>
  );
}
