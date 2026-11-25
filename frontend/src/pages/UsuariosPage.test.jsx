import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AppRoutes } from '../App.jsx';
import { AuthProvider } from '../context/AuthContext.jsx';
import { tokenStorage } from '../services/tokenStorage.js';
import { USUARIO, jsonResponse, problemaResponse } from '../test/respuestas.js';

const COORDINACION = {
  ...USUARIO,
  id: '00000000-0000-4000-8000-0000000000c1',
  nombre_completo: 'Rosa Huamán Coordinadora',
  correo: 'coordinacion@ecoalert.pe',
  rol: 'coordinacion',
};
const NUEVA = {
  ...USUARIO,
  id: '00000000-0000-4000-8000-0000000000a2',
  nombre_completo: 'Luis Condori',
  correo: 'luis.condori@ecoalert.pe',
  debe_cambiar_password: true,
};

/**
 * Simula el backend: GET /auth/me devuelve la sesión indicada y el resto de rutas se resuelve con `rutas`,
 * un mapa "MÉTODO ruta" → función que devuelve la Response.
 */
function backend(sesion, rutas) {
  return vi.fn().mockImplementation(async (url, init) => {
    const ruta = new URL(url, 'http://localhost').pathname.replace('/api/v1', '');
    if (ruta === '/auth/me') return jsonResponse({ usuario: sesion, ultima_actividad: '2026-11-24T10:00:00Z' });
    const manejador = rutas[`${init.method} ${ruta}`];
    if (!manejador) throw new Error(`Ruta no simulada: ${init.method} ${ruta}`);
    return manejador(url, init);
  });
}

function renderizarEn(ruta) {
  tokenStorage.guardar('jwt', 3600);
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('UsuariosPage (RF-02)', () => {
  it('lista las cuentas y filtra por estado', async () => {
    const fetchMock = backend(COORDINACION, {
      'GET /usuarios': async () => jsonResponse([COORDINACION, USUARIO]),
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/usuarios');

    expect(await screen.findByText('ana.quispe@ecoalert.pe')).toBeInTheDocument();
    expect(screen.getByText('(tu cuenta)')).toBeInTheDocument();

    await usuario.click(screen.getByRole('button', { name: 'Desactivadas' }));
    await vi.waitFor(() => expect(fetchMock.mock.calls.at(-1)[0]).toBe('/api/v1/usuarios?activo=false'));
  });

  it('crea una cuenta con Idempotency-Key y muestra la confirmación (RF-02-AC-1)', async () => {
    let listado = [COORDINACION];
    const fetchMock = backend(COORDINACION, {
      'GET /usuarios': async () => jsonResponse(listado),
      'POST /usuarios': async () => {
        listado = [COORDINACION, NUEVA];
        return jsonResponse(NUEVA, { status: 201 });
      },
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/usuarios');
    await screen.findByText('coordinacion@ecoalert.pe');

    await usuario.click(screen.getByRole('button', { name: 'Nueva cuenta' }));
    await usuario.type(screen.getByLabelText('Nombre completo'), 'Luis Condori');
    await usuario.type(screen.getByLabelText('Correo'), 'luis.condori@ecoalert.pe');
    await usuario.type(screen.getByLabelText('Contraseña temporal'), 'Temporal-2026!');
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }));

    expect(await screen.findByText(/Cuenta creada para Luis Condori/)).toBeInTheDocument();
    expect(screen.queryByLabelText('Nombre completo')).not.toBeInTheDocument();
    expect(await screen.findByText('luis.condori@ecoalert.pe')).toBeInTheDocument();

    const [, init] = fetchMock.mock.calls.find(([, i]) => i.method === 'POST');
    expect(init.headers.get('Idempotency-Key')).toMatch(/^[0-9a-f-]{36}$/);
    expect(JSON.parse(init.body)).toEqual({
      nombre_completo: 'Luis Condori',
      correo: 'luis.condori@ecoalert.pe',
      rol: 'analista_sig',
      password_temporal: 'Temporal-2026!',
    });
  });

  it('rechaza en el cliente una contraseña temporal de 11 caracteres (RF-02-AC-3)', async () => {
    const fetchMock = backend(COORDINACION, { 'GET /usuarios': async () => jsonResponse([COORDINACION]) });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/usuarios');
    await screen.findByText('coordinacion@ecoalert.pe');

    await usuario.click(screen.getByRole('button', { name: 'Nueva cuenta' }));
    await usuario.type(screen.getByLabelText('Nombre completo'), 'Luis Condori');
    await usuario.type(screen.getByLabelText('Correo'), 'luis.condori@ecoalert.pe');
    await usuario.type(screen.getByLabelText('Contraseña temporal'), '12345678901');
    await usuario.click(screen.getByRole('button', { name: 'Crear cuenta' }));

    expect(screen.getByText('La contraseña temporal debe tener al menos 12 caracteres.')).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([, i]) => i.method === 'POST')).toBe(false);
  });

  it('muestra el error del servidor al desactivar la última coordinación (RF-02-AC-8)', async () => {
    const fetchMock = backend(COORDINACION, {
      'GET /usuarios': async () => jsonResponse([COORDINACION]),
      [`PATCH /usuarios/${COORDINACION.id}`]: async () =>
        problemaResponse(409, 'ULTIMA_COORDINACION', 'No se puede desactivar la última cuenta de coordinación'),
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/usuarios');
    await screen.findByText('coordinacion@ecoalert.pe');

    await usuario.click(screen.getByRole('button', { name: 'Desactivar coordinacion@ecoalert.pe' }));
    await usuario.click(screen.getByRole('button', { name: 'Desactivar cuenta de coordinacion@ecoalert.pe' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('No se puede desactivar la última cuenta de coordinación');
    const [, init] = fetchMock.mock.calls.find(([, i]) => i.method === 'PATCH');
    expect(init.headers.get('Content-Type')).toBe('application/merge-patch+json');
    expect(JSON.parse(init.body)).toEqual({ activo: false });
  });

  it('edita solo los campos que cambiaron', async () => {
    let listado = [COORDINACION, USUARIO];
    const fetchMock = backend(COORDINACION, {
      'GET /usuarios': async () => jsonResponse(listado),
      [`PATCH /usuarios/${USUARIO.id}`]: async () => {
        listado = [COORDINACION, { ...USUARIO, rol: 'coordinacion' }];
        return jsonResponse(listado[1]);
      },
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/usuarios');
    await screen.findByText('ana.quispe@ecoalert.pe');

    await usuario.click(screen.getByRole('button', { name: 'Editar ana.quispe@ecoalert.pe' }));
    await usuario.selectOptions(screen.getByLabelText('Rol de ana.quispe@ecoalert.pe'), 'coordinacion');
    await usuario.click(screen.getByRole('button', { name: 'Guardar' }));

    expect(await screen.findByText('Cuenta de Ana Quispe Mamani actualizada.')).toBeInTheDocument();
    const [, init] = fetchMock.mock.calls.find(([, i]) => i.method === 'PATCH');
    expect(JSON.parse(init.body)).toEqual({ rol: 'coordinacion' });
    const fila = screen.getByText('ana.quispe@ecoalert.pe').closest('tr');
    expect(within(fila).getByText('Coordinación')).toBeInTheDocument();
  });

  it('un Analista SIG no ve la opción en el menú ni puede usar la pantalla (RF-02-AC-10)', async () => {
    const fetchMock = backend(USUARIO, {});
    vi.stubGlobal('fetch', fetchMock);
    renderizarEn('/usuarios');

    expect(await screen.findByText('Sección exclusiva de Coordinación')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Usuarios' })).not.toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => url.includes('/usuarios'))).toBe(false);
  });

  it('Coordinación sí ve la opción "Usuarios" en el menú', async () => {
    vi.stubGlobal('fetch', backend(COORDINACION, {}));
    renderizarEn('/dashboard');
    expect(await screen.findByRole('link', { name: 'Usuarios' })).toBeInTheDocument();
  });
});
