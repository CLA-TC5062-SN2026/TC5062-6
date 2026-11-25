// Mensaje de error visible para el usuario, con acción opcional de reintento.
// role="alert" hace que el lector de pantalla lo anuncie en cuanto aparece (WCAG 2.1, 4.1.3).

import Button from './Button.jsx';

export default function ErrorAlert({ titulo = 'No se pudo completar la operación', mensaje, onReintentar }) {
  if (!mensaje) return null;
  return (
    <div role="alert" className="border-l-4 border-peligro bg-peligro-tenue px-4 py-3 text-peligro-texto">
      <p className="font-semibold">{titulo}</p>
      <p className="mt-0.5">{mensaje}</p>
      {onReintentar && (
        <div className="mt-3">
          <Button variant="secondary" onClick={onReintentar}>
            Reintentar
          </Button>
        </div>
      )}
    </div>
  );
}
