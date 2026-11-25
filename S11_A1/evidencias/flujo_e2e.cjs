// Prueba E2E del flujo de la demo (S11-A1) contra el sistema real: Vite/vite preview + FastAPI + PostGIS.
// Recorre: redirección sin sesión, login fallido (401), login, alertas, CRUD de usuarios, error 409 de la
// última coordinación, primer ingreso con contraseña temporal + cambio obligatorio y baja lógica.
// Guarda capturas y falla si la consola del navegador tiene errores distintos de los 401/409 provocados.
//
// Uso (Playwright no es dependencia del proyecto; se instala aparte, en una carpeta temporal):
//   mkdir /tmp/e2e && cd /tmp/e2e && npm i playwright@1.60.0 && npx playwright install chromium
//   cp <repo>/S11_A1/evidencias/flujo_e2e.cjs . && node flujo_e2e.cjs <urlBase> <dirCapturas> <passwordCoordinacion>
// Requiere la cuenta coordinacion@ecoalert.pe, la semilla `python -m scripts.sembrar_demo` y que la cuenta de
// Coordinación sea la única activa de su rol (para provocar el 409). Crea una cuenta nueva en cada corrida.
const { chromium } = require('playwright');

const [base, dir, pw] = process.argv.slice(2);
const NUEVO = { nombre: 'Jorge Ccahuana Tito', correo: `jorge.ccahuana.${Date.now() % 100000}@ecoalert.pe` };
const TEMPORAL = 'Temporal-Tambo-2026';
const PROPIA = 'Jorge-Propia-2026!';

(async () => {
  const browser = await chromium.launch(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {});
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 }, locale: 'es-PE' });
  const erroresConsola = [];
  page.on('console', (m) => { if (m.type() === 'error') erroresConsola.push(m.text() + ' @ ' + (m.location().url || '?')); });
  page.on('pageerror', (e) => erroresConsola.push(String(e)));
  page.on('response', (r) => { if (r.status() >= 400) console.log('  ·', r.status(), r.request().method(), r.url()); });
  const foto = (n) => page.screenshot({ path: `${dir}/${n}.png`, fullPage: true });
  const paso = (t) => console.log('✓', t);

  async function login(correo, password) {
    await page.goto(`${base}/login`);
    await page.getByLabel('Correo electrónico').fill(correo);
    await page.getByLabel('Contraseña', { exact: true }).fill(password);
    await page.getByRole('button', { name: 'Ingresar' }).click();
  }
  async function logout() {
    await page.getByRole('button', { name: 'Cerrar sesión' }).click();
    await page.getByRole('heading', { name: 'Iniciar sesión' }).waitFor();
  }

  // Codespaces muestra un aviso de GitHub la primera vez que se abre un puerto público.
  await page.goto(`${base}/`);
  const continuar = page.getByRole('button', { name: 'Continue', exact: true });
  if (await continuar.count()) { await continuar.click(); await page.waitForURL(`${base}/**`); paso('aviso de Codespaces aceptado'); }

  // 1. Ruta protegida sin sesión → login
  await page.goto(`${base}/dashboard`);
  await page.getByRole('heading', { name: 'Iniciar sesión' }).waitFor();
  paso('sin sesión redirige a /login');
  await foto('01-login');

  // 2. Error manejado: credenciales incorrectas
  await login('coordinacion@ecoalert.pe', 'contraseña-equivocada');
  await page.getByText('Usuario o contraseña incorrectos').waitFor();
  paso('credenciales incorrectas → 401 con mensaje genérico');

  // 3. Login de Coordinación
  await login('coordinacion@ecoalert.pe', pw);
  await page.getByRole('heading', { name: 'Panel', exact: true }).waitFor();
  await page.getByRole('heading', { name: 'Zonas por superficie alertada' }).waitFor();
  paso('login de Coordinación');
  await foto('02-panel-coordinacion');

  // 4. Alertas (datos de la semilla)
  await page.getByRole('link', { name: 'Alertas', exact: true }).click();
  await page.getByText('24 alertas encontradas').waitFor();
  paso('alertas: 24 desde PostGIS');
  await foto('03-alertas');

  // 5. CRUD de usuarios
  await page.getByRole('link', { name: 'Usuarios', exact: true }).click();
  await page.getByText('analista.demo@ecoalert.pe', { exact: true }).waitFor();
  paso('lista de usuarios (Read)');

  await page.getByRole('button', { name: 'Nueva cuenta' }).click();
  await page.getByLabel('Nombre completo').fill(NUEVO.nombre);
  await page.getByLabel('Correo', { exact: true }).fill(NUEVO.correo);
  await page.getByLabel('Contraseña temporal').fill('corta');
  await page.getByRole('button', { name: 'Crear cuenta' }).click();
  await page.getByText('La contraseña temporal debe tener al menos 12 caracteres.').waitFor();
  paso('validación de contraseña temporal en el cliente');
  await page.getByLabel('Contraseña temporal').fill(TEMPORAL);
  await page.getByRole('button', { name: 'Crear cuenta' }).click();
  await page.getByText(`Cuenta creada para ${NUEVO.nombre}`).waitFor();
  await page.getByText(NUEVO.correo, { exact: true }).waitFor();
  paso('cuenta creada (Create)');
  await foto('04-usuarios-creado');

  await page.getByRole('button', { name: `Editar ${NUEVO.correo}` }).click();
  await page.getByLabel(`Nombre de ${NUEVO.correo}`).fill(`${NUEVO.nombre} (Brigada Malinowski)`);
  await page.getByRole('button', { name: 'Guardar' }).click();
  await page.getByText(`Cuenta de ${NUEVO.nombre} (Brigada Malinowski) actualizada.`).waitFor();
  paso('nombre actualizado (Update, PATCH)');

  // 6. Error manejado: desactivar la última coordinación → 409
  await page.getByRole('button', { name: 'Desactivar coordinacion@ecoalert.pe' }).click();
  await page.getByRole('button', { name: 'Desactivar cuenta de coordinacion@ecoalert.pe' }).click();
  await page.getByText('No se puede desactivar la última cuenta de coordinación').waitFor();
  paso('409 ULTIMA_COORDINACION mostrado');
  await foto('05-error-ultima-coordinacion');

  // 7. Primer ingreso de la cuenta nueva: contraseña temporal → cambio obligatorio
  await logout();
  await login(NUEVO.correo, TEMPORAL);
  await page.getByText('Tu cuenta tiene una contraseña temporal').waitFor();
  await page.getByRole('link', { name: 'Usuarios', exact: true }).waitFor({ state: 'detached', timeout: 1000 }).catch(() => {});
  if (await page.getByRole('link', { name: 'Usuarios', exact: true }).count()) throw new Error('Analista ve el menú Usuarios');
  paso('analista con contraseña temporal: aviso y sin menú Usuarios');
  await page.getByRole('link', { name: 'Cambiar mi contraseña' }).click();
  await page.getByLabel('Contraseña actual', { exact: true }).fill(TEMPORAL);
  await page.getByLabel('Contraseña nueva', { exact: true }).fill(PROPIA);
  await page.getByLabel('Repite la contraseña nueva').fill(PROPIA);
  await foto('06-cambiar-password');
  await page.getByRole('button', { name: 'Guardar contraseña' }).click();
  await page.getByRole('heading', { name: 'Panel', exact: true }).waitFor();
  if (await page.getByText('Tu cuenta tiene una contraseña temporal').count()) throw new Error('aviso persiste');
  paso('contraseña propia definida (RF-02-AC-4)');

  // 8. Baja lógica (Delete lógico): Coordinación desactiva la cuenta y ya no puede ingresar
  await logout();
  await login('coordinacion@ecoalert.pe', pw);
  await page.getByRole('link', { name: 'Usuarios', exact: true }).click();
  await page.getByRole('button', { name: `Desactivar ${NUEVO.correo}` }).click();
  await page.getByRole('button', { name: `Desactivar cuenta de ${NUEVO.correo}` }).click();
  await page.getByText('desactivada; sus sesiones abiertas se cerraron.').waitFor();
  paso('cuenta desactivada (baja lógica)');
  await foto('07-usuario-desactivado');
  await logout();
  await login(NUEVO.correo, PROPIA);
  await page.getByText('Usuario o contraseña incorrectos').waitFor();
  paso('cuenta desactivada no puede iniciar sesión (RF-02-AC-5)');

  // El navegador registra cada respuesta 4xx como "Failed to load resource". Los 401 (credenciales
  // incorrectas) y el 409 (última coordinación) son los errores provocados a propósito; cualquier otro falla.
  const esperado = /Failed to load resource: the server responded with a status of (401|409)/;
  const inesperados = erroresConsola.filter((m) => !esperado.test(m));
  console.log('Errores de consola esperados (401/409):', erroresConsola.length - inesperados.length);
  console.log('Errores de consola inesperados:', inesperados.length ? inesperados : 'ninguno');
  await browser.close();
  if (inesperados.length) process.exit(1);
})().catch(async (e) => { console.error('✗', e.message); process.exit(1); });
