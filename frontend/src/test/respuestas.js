// Utilidades para simular respuestas del backend en las pruebas.

export function jsonResponse(cuerpo, { status = 200, headers = {} } = {}) {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  });
}

export function problemaResponse(status, codigo, mensaje, headers = {}) {
  return new Response(JSON.stringify({ type: 'about:blank', status, codigo, mensaje, detail: mensaje }), {
    status,
    headers: { 'Content-Type': 'application/problem+json', ...headers },
  });
}

export const USUARIO = {
  id: '00000000-0000-4000-8000-000000000001',
  nombre_completo: 'Ana Quispe Mamani',
  correo: 'ana.quispe@ecoalert.pe',
  rol: 'analista_sig',
  activo: true,
  debe_cambiar_password: false,
  creado_en: '2026-09-01T08:00:00Z',
};

export const SESION_CREADA = {
  access_token: 'header.payload.firma',
  token_type: 'bearer',
  expires_in: 28800,
  inactividad_max_segundos: 1800,
  usuario: USUARIO,
};
