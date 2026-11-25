// Botón del sistema visual. Variantes por intención, no por color:
// primary = acción principal, secondary = alternativa neutra, texto = acción de fila, peligro = acción destructiva.

const BASE = `
  inline-flex min-h-11 items-center justify-center gap-2
  rounded px-4 font-semibold
  transition-colors motion-reduce:transition-none
  disabled:cursor-not-allowed disabled:opacity-60
`;

const VARIANTES = {
  primary: 'bg-dosel text-white hover:bg-dosel-oscuro',
  secondary: 'border border-linea-fuerte bg-white text-tinta hover:bg-papel',
  texto: 'px-3 text-dosel hover:bg-dosel-tenue',
  peligro: 'bg-peligro text-white hover:bg-peligro-texto',
};

export default function Button({
  children,
  variant = 'primary',
  loading = false,
  disabled = false,
  onClick,
  type = 'button',
  className = '',
  ...props
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      aria-busy={loading}
      className={`${BASE} ${VARIANTES[variant] ?? VARIANTES.primary} ${className}`}
      {...props}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent motion-reduce:animate-none"
        />
      )}
      {loading ? 'Cargando...' : children}
    </button>
  );
}
