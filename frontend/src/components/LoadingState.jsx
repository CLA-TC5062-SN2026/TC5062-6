// Indicador de carga accesible: role="status" lo anuncia a lectores de pantalla (WCAG 2.1, 4.1.3).

export default function LoadingState({ mensaje = 'Cargando…', pantallaCompleta = false }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex items-center justify-center gap-3 text-gray-700 ${
        pantallaCompleta ? 'min-h-screen bg-gray-100' : 'py-10'
      }`}
    >
      <span
        aria-hidden="true"
        className="h-6 w-6 animate-spin rounded-full border-4 border-green-700 border-t-transparent"
      />
      <span>{mensaje}</span>
    </div>
  );
}
