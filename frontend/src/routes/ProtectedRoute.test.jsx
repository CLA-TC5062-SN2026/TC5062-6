import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AppRoutes } from '../App.jsx';
import { AuthProvider } from '../context/AuthContext.jsx';
import { tokenStorage } from '../services/tokenStorage.js';
import { SESION_CREADA, USUARIO, jsonResponse, problemaResponse } from '../test/respuestas.js';

function renderizarEn(ruta) {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('flujo de autenticación y ruta protegida', () => {
  it('sin sesión, una ruta protegida redirige al login', async () => {
    vi.stubGlobal('fetch', vi.fn());
    renderizarEn('/dashboard');
    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it('con un token guardado, confirma la sesión con /auth/me y muestra la ruta protegida', async () => {
    tokenStorage.guardar('jwt', 3600);
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () => jsonResponse({ usuario: USUARIO, ultima_actividad: 'x' })));
    renderizarEn('/dashboard');
    expect(screen.getByRole('status')).toHaveTextContent('Verificando tu sesión');
    expect(await screen.findByRole('heading', { name: 'Panel de monitoreo ambiental' })).toBeInTheDocument();
  });

  it('si el servidor rechaza el token guardado, vuelve al login y explica por qué', async () => {
    tokenStorage.guardar('jwt-revocado', 3600);
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () =>
      problemaResponse(401, 'NO_AUTENTICADO', 'La sesión expiró o no es válida. Inicia sesión de nuevo.'),
    ));
    renderizarEn('/alertas');
    expect(await screen.findByText('La sesión expiró o no es válida. Inicia sesión de nuevo.')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument();
  });

  it('login exitoso redirige a la ruta protegida que se había pedido', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(jsonResponse(SESION_CREADA)).mockImplementation(async () =>
      jsonResponse({ total: 0, limite: 10, desplazamiento: 0, alertas: [] }),
    ));
    const usuario = userEvent.setup();
    renderizarEn('/alertas');

    await usuario.type(await screen.findByLabelText('Correo electrónico'), 'ana.quispe@ecoalert.pe');
    await usuario.type(screen.getByLabelText('Contraseña'), 'clave-segura-2026');
    await usuario.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(await screen.findByRole('heading', { name: 'Alertas de deforestación' })).toBeInTheDocument();
    expect(tokenStorage.obtener()).toBe(SESION_CREADA.access_token);
  });

  it('valida el formulario antes de llamar a la API', async () => {
    vi.stubGlobal('fetch', vi.fn());
    const usuario = userEvent.setup();
    renderizarEn('/login');

    await usuario.click(await screen.findByRole('button', { name: 'Ingresar' }));

    expect(screen.getByText('Ingresa tu correo electrónico.')).toBeInTheDocument();
    expect(screen.getByText('Ingresa tu contraseña.')).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it('muestra el error del servidor cuando las credenciales son incorrectas', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () =>
      problemaResponse(401, 'CREDENCIALES_INVALIDAS', 'Usuario o contraseña incorrectos'),
    ));
    const usuario = userEvent.setup();
    renderizarEn('/login');

    await usuario.type(await screen.findByLabelText('Correo electrónico'), 'ana.quispe@ecoalert.pe');
    await usuario.type(screen.getByLabelText('Contraseña'), 'incorrecta');
    await usuario.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(await screen.findByText('Usuario o contraseña incorrectos')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toHaveValue('');
  });
});
