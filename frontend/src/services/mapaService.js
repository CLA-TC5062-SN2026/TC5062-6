// Servicio de las capas del mapa (contrato: tag "Mapa", RF-06).

import { api } from './api.js';

/**
 * GET /mapa/capas/{capaMapaId}/elementos — operationId obtenerElementosCapa. Roles: analista_sig, coordinacion.
 * @param {'zonas_cambio'|'alertas_geobosques'|'limite_reserva'|'zona_amortiguamiento'|'rios'|'catastro_minero'} capa
 * @returns {Promise<{type: 'FeatureCollection', features: Array<object>}>} GeoJSON en EPSG:4326 (RFC 7946)
 */
function elementos(capa, { signal } = {}) {
  return api.get(`/mapa/capas/${encodeURIComponent(capa)}/elementos`, { signal });
}

export const mapaService = { elementos };
