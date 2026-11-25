import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AppRoutes } from '../App.jsx';
import { AuthProvider } from '../context/AuthContext.jsx';
import { tokenStorage } from '../services/tokenStorage.js';
import { USUARIO, jsonResponse, problemaResponse } from '../test/respuestas.js';

const TEMPORAL = { ...USUARIO, debe_cambiar_password: true };

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

async function completar(usuario, { actual, nueva, confirmacion = nueva }) {
  await usuario.type(await screen.findByLabelText('Contraseña actual'), actual);
  await usuario.type(screen.getByLabelText('Contraseña nueva'), nueva);
  await usuario.type(screen.getByLabelText('Repite la contraseña nueva'), confirmacion);
  await usuario.click(screen.getByRole('button', { name: 'Guardar contraseña' }));
}

describe('CambiarPasswordPage (RF-02-AC-4)', () => {
  it('cambia la contraseña temporal y vuelve al panel sin el aviso', async () => {
    let actual = TEMPORAL;
    const fetchMock = vi.fn().mockImplementation(async (url, init) => {
      if (url.endsWith('/auth/me')) return jsonResponse({ usuario: actual, ultima_actividad: 'x' });
      if (url.endsWith('/auth/password') && init.method === 'PUT') {
        actual = USUARIO;
        return new Response(null, { status: 204 });
      }
      throw new Error(`Ruta no simulada: ${url}`);
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/dashboard');

    await usuario.click(await screen.findByRole('link', { name: 'Cambiar mi contraseña' }));
    await completar(usuario, { actual: 'Temporal-2026!', nueva: 'Mi-clave-propia-2026' });

    expect(await screen.findByRole('heading', { name: 'Panel' })).toBeInTheDocument();
    expect(screen.queryByText(/contraseña temporal/)).not.toBeInTheDocument();
    const [, init] = fetchMock.mock.calls.find(([, i]) => i.method === 'PUT');
    expect(JSON.parse(init.body)).toEqual({ password_actual: 'Temporal-2026!', password_nueva: 'Mi-clave-propia-2026' });
  });

  it('valida en el cliente la longitud y la confirmación', async () => {
    const fetchMock = vi.fn().mockImplementation(async () => jsonResponse({ usuario: TEMPORAL, ultima_actividad: 'x' }));
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    renderizarEn('/cambiar-password');

    await completar(usuario, { actual: 'Temporal-2026!', nueva: 'corta', confirmacion: 'otra' });
    expect(screen.getByText('Debe tener al menos 12 caracteres.')).toBeInTheDocument();
    expect(screen.getByText('Las contraseñas no coinciden.')).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([, i]) => i?.method === 'PUT')).toBe(false);
  });

  it('muestra el error del servidor si la contraseña actual es incorrecta', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async (url) =>
      url.endsWith('/auth/me')
        ? jsonResponse({ usuario: TEMPORAL, ultima_actividad: 'x' })
        : problemaResponse(422, 'VALIDACION', 'La contraseña actual no es correcta'),
    ));
    const usuario = userEvent.setup();
    renderizarEn('/cambiar-password');

    await completar(usuario, { actual: 'equivocada-123', nueva: 'Mi-clave-propia-2026' });
    expect(await screen.findByRole('alert')).toHaveTextContent('La contraseña actual no es correcta');
  });
});
