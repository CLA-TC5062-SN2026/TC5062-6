# Context

`AuthContext.jsx` comparte la sesión entre vistas: usuario autenticado, estado de verificación
(`verificando`, `autenticado`, `anonimo`), `login()` y `logout()`. El token no vive aquí: lo administra
`services/tokenStorage.js` y lo agrega el interceptor de `services/api.js`.
