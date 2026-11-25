// Servicio del recurso Usuarios (contrato: tag "Usuarios", RF-02). Todas las operaciones son de Coordinación.
//
// No hay "eliminar": el SRS prohíbe borrar cuentas para conservar la autoría en el historial (RF-02-AC-7,
// la API responde 405). La baja es lógica: PATCH { activo: false }, que además revoca las sesiones abiertas.

import { api } from './api.js';

// RFC 7396: el contrato exige este tipo en PATCH /usuarios/{id} (415 con application/json).
const MERGE_PATCH = { 'Content-Type': 'application/merge-patch+json' };

/** Genera una Idempotency-Key (UUID v4) para POST /usuarios. */
export function nuevaClaveIdempotencia() {
  return globalThis.crypto.randomUUID();
}

/**
 * GET /usuarios — operationId listarUsuarios.
 * @param {{activo?: boolean, signal?: AbortSignal}} opciones  sin `activo` devuelve todas las cuentas
 */
function listar({ activo, signal } = {}) {
  return api.get('/usuarios', { signal, params: { activo } });
}

/**
 * POST /usuarios — operationId crearUsuario. La cuenta nace activa y con contraseña temporal (RF-02-AC-1).
 * La misma `idempotencyKey` con el mismo cuerpo devuelve la respuesta original: un reintento tras un corte
 * de red no crea dos cuentas.
 */
function crear({ nombreCompleto, correo, rol, passwordTemporal }, { idempotencyKey }) {
  return api.post(
    '/usuarios',
    {
      nombre_completo: nombreCompleto.trim(),
      correo: correo.trim(),
      rol,
      password_temporal: passwordTemporal,
    },
    { headers: { 'Idempotency-Key': idempotencyKey } },
  );
}

/**
 * PATCH /usuarios/{usuarioId} — operationId actualizarUsuario. Solo se envían los campos que cambian.
 * @param {string} id
 * @param {{nombre_completo?: string, rol?: string, activo?: boolean}} cambios
 */
function actualizar(id, cambios) {
  return api.patch(`/usuarios/${encodeURIComponent(id)}`, cambios, { headers: MERGE_PATCH });
}

export const usuariosService = {
  listar,
  crear,
  actualizar,
  desactivar: (id) => actualizar(id, { activo: false }),
  reactivar: (id) => actualizar(id, { activo: true }),
};
