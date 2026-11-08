// Estado de una consulta a la API: datos, carga, error y reintento.
// Cancela la petición anterior cuando cambian los parámetros o el componente se desmonta,
// así una respuesta lenta nunca sobrescribe una más reciente.

import { useCallback, useEffect, useRef, useState } from 'react';
import { comoApiError } from '../services/apiError.js';

/**
 * @param {(opciones: {signal: AbortSignal}) => Promise<any>} consultar  función del servicio a ejecutar
 * @param {Array<unknown>} dependencias  valores que, al cambiar, repiten la consulta
 */
export function useApiQuery(consultar, dependencias) {
  const [estado, setEstado] = useState({ datos: null, error: null, cargando: true });
  const [intento, setIntento] = useState(0);
  const consultarRef = useRef(consultar);
  consultarRef.current = consultar;

  useEffect(() => {
    const controlador = new AbortController();
    setEstado((previo) => ({ ...previo, cargando: true, error: null }));
    consultarRef
      .current({ signal: controlador.signal })
      .then((datos) => {
        if (!controlador.signal.aborted) setEstado({ datos, error: null, cargando: false });
      })
      .catch((error) => {
        if (!controlador.signal.aborted) {
          setEstado((previo) => ({ ...previo, error: comoApiError(error), cargando: false }));
        }
      });
    return () => controlador.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- las dependencias las declara quien llama
  }, [...dependencias, intento]);

  const recargar = useCallback(() => setIntento((n) => n + 1), []);
  return { ...estado, recargar };
}
