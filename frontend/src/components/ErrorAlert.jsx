// Mensaje de error visible para el usuario, con acción opcional de reintento.
// role="alert" hace que el lector de pantalla lo anuncie en cuanto aparece (WCAG 2.1, 4.1.3).

import Button from './Button.jsx';

export default function ErrorAlert({ titulo = 'No se pudo completar la operación', mensaje, onReintentar }) {
  if (!mensaje) return null;
  return (
    <div role="alert" className="rounded-md border border-red-300 bg-red-50 p-4 text-red-900">
      <p className="font-semibold">{titulo}</p>
      <p className="mt-1 text-sm">{mensaje}</p>
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
