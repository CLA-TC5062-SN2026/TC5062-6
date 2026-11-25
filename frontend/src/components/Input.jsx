import { useId } from 'react';

/**
 * Campo de texto con etiqueta visible y error asociado (aria-describedby).
 * `sufijo` coloca un control dentro del borde del campo, a la derecha (p. ej. Mostrar/Ocultar contraseña).
 */
export default function Input({
  label,
  value,
  onChange,
  placeholder = '',
  type = 'text',
  error = '',
  sufijo = null,
  ...props
}) {
  const id = useId();
  const errorId = `${id}-error`;
  const borde = error ? 'border-2 border-peligro' : 'border border-linea-fuerte';

  const campo = (
    <input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      aria-invalid={Boolean(error)}
      aria-describedby={error ? errorId : undefined}
      className={
        sufijo
          ? 'h-full min-w-0 flex-1 rounded bg-transparent px-3 text-tinta placeholder:text-tinta-suave focus:outline-none'
          : `h-11 rounded bg-white px-3 text-tinta placeholder:text-tinta-suave ${borde}`
      }
      {...props}
    />
  );

  return (
    <div className="flex w-full flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-semibold text-tinta">
        {label}
      </label>

      {sufijo ? (
        <div className={`flex h-11 items-center rounded bg-white focus-within:outline-3 focus-within:outline-offset-2 focus-within:outline-rio ${borde}`}>
          {campo}
          {sufijo}
        </div>
      ) : (
        campo
      )}

      {error && (
        <span id={errorId} role="alert" className="text-sm text-peligro">
          {error}
        </span>
      )}
    </div>
  );
}
