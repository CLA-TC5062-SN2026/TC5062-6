// Servicio del recurso Alertas (contrato: tag "Alertas", RF-04).

import { api } from './api.js';

export const LIMITE_MAXIMO = 500; // components/parameters/Limite del contrato

/**
 * GET /alertas — operationId listarAlertas. Roles: analista_sig, coordinacion.
 * Traduce los nombres del frontend (camelCase) a los parámetros del contrato (snake_case).
 * @returns {Promise<{total: number, limite: number, desplazamiento: number, alertas: Array<object>}>}
 */
function listar({ zona, presenteEnUltimaCarga, limite = 20, desplazamiento = 0, signal } = {}) {
  return api.get('/alertas', {
    signal,
    params: {
      zona: zona?.trim().toUpperCase(),
      presente_en_ultima_carga: presenteEnUltimaCarga,
      limite: Math.min(Math.max(limite, 1), LIMITE_MAXIMO),
      desplazamiento: Math.max(desplazamiento, 0),
    },
  });
}

export const alertasService = { listar };
