// Almacenamiento del JWT en el cliente.
//
// Decisión (ver S07_S08_A2/capa_servicios.md):
// - sessionStorage, no localStorage: el token desaparece al cerrar la pestaña y no se comparte entre
//   pestañas, lo que reduce la ventana de exposición (OWASP HTML5 Security Cheat Sheet).
// - Copia en memoria: las lecturas no tocan el almacenamiento y la app sigue funcionando si el navegador
//   lo bloquea (modo privado, políticas de la organización).
// - Se guarda también la hora de expiración calculada con `expires_in`: un token vencido no se envía.
// - Nunca se registra el token en la consola ni se guarda la contraseña.

const CLAVE = 'ecoalert.sesion';
// Margen para no enviar un token que vencería en tránsito.
const MARGEN_EXPIRACION_MS = 5000;

let enMemoria = null;

function almacenamiento() {
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

function vigente(sesion, ahora = Date.now()) {
  return Boolean(
    sesion
      && typeof sesion.token === 'string'
      && sesion.token.length > 0
      && Number.isFinite(sesion.expiraEn)
      && sesion.expiraEn - MARGEN_EXPIRACION_MS > ahora,
  );
}

function leerPersistida() {
  try {
    const crudo = almacenamiento()?.getItem(CLAVE);
    return crudo ? JSON.parse(crudo) : null;
  } catch {
    return null;
  }
}

export const tokenStorage = {
  /** Guarda el token y su expiración absoluta (expiresInSegundos viene de `SesionCreada.expires_in`). */
  guardar(token, expiresInSegundos) {
    enMemoria = { token, expiraEn: Date.now() + expiresInSegundos * 1000 };
    try {
      almacenamiento()?.setItem(CLAVE, JSON.stringify(enMemoria));
    } catch {
      // Sin almacenamiento disponible la sesión dura lo que la pestaña abierta: degradación aceptable.
    }
  },

  /** Devuelve el token vigente o null. Si venció, lo elimina. */
  obtener() {
    const sesion = enMemoria ?? leerPersistida();
    if (!vigente(sesion)) {
      this.limpiar();
      return null;
    }
    enMemoria = sesion;
    return sesion.token;
  },

  limpiar() {
    enMemoria = null;
    try {
      almacenamiento()?.removeItem(CLAVE);
    } catch {
      // Nada que limpiar si el almacenamiento no está disponible.
    }
  },
};
