// Control segmentado: un grupo de botones excluyentes con aria-pressed.
// Se usa para filtros de pocas opciones, donde un <select> oculta las alternativas tras un clic.

export default function Segmento({ etiqueta, etiquetaId, opciones, valor, onCambiar }) {
  return (
    <div
      role="group"
      aria-label={etiquetaId ? undefined : etiqueta}
      aria-labelledby={etiquetaId}
      className="inline-flex overflow-hidden rounded border border-linea-fuerte bg-white">
      {opciones.map((opcion, indice) => {
        const activa = opcion.valor === valor;
        return (
          <button
            key={opcion.valor}
            type="button"
            aria-pressed={activa}
            onClick={() => onCambiar(opcion.valor)}
            className={`h-10 px-4 text-sm ${indice > 0 ? 'border-l border-linea-fuerte' : ''} ${
              activa ? 'bg-dosel font-semibold text-white' : 'bg-white font-medium text-tinta hover:bg-papel'
            }`}
          >
            {opcion.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
