import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { jsonResponse } from '../test/respuestas.js';
import AlertasPage from './AlertasPage.jsx';

const PAGINA = {
  total: 1,
  limite: 10,
  desplazamiento: 0,
  alertas: [
    {
      id: '10000000-0000-4000-8000-000000000001',
      fuente: 'GeoBosques',
      codigo: 'GB-2026-0001',
      fecha_deteccion: '2026-10-01',
      fecha_ingesta: '2026-10-02T09:00:00Z',
      presente_en_ultima_carga: true,
      zona_codigo: 'EA-2026-001',
      area_ha: 1.2,
    },
  ],
};

function renderizar() {
  return render(
    <MemoryRouter>
      <AlertasPage />
    </MemoryRouter>,
  );
}

describe('AlertasPage', () => {
  it('muestra el estado de carga y después las alertas del backend', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () => jsonResponse(PAGINA)));
    renderizar();

    expect(screen.getByRole('status')).toHaveTextContent('Cargando alertas');
    expect(await screen.findByRole('cell', { name: 'GB-2026-0001' })).toBeInTheDocument();
    expect(screen.getByText('1 alerta encontrada')).toBeInTheDocument();
    expect(screen.getByRole('cell', { name: '1.20' })).toBeInTheDocument();
    expect(fetch.mock.calls[0][0]).toBe('/api/v1/alertas?limite=10&desplazamiento=0');
  });

  it('muestra un error comprensible y permite reintentar', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockImplementation(async () => jsonResponse(PAGINA)));
    const usuario = userEvent.setup();
    renderizar();

    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con el servidor');
    await usuario.click(screen.getByRole('button', { name: 'Reintentar' }));
    expect(await screen.findByRole('cell', { name: 'GB-2026-0001' })).toBeInTheDocument();
  });

  it('valida el código de zona en el cliente y envía el filtro normalizado', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () => jsonResponse(PAGINA)));
    const usuario = userEvent.setup();
    renderizar();
    await screen.findByRole('cell', { name: 'GB-2026-0001' });

    const campo = screen.getByLabelText('Código de zona');
    await usuario.type(campo, 'zona-1');
    await usuario.click(screen.getByRole('button', { name: 'Buscar' }));
    expect(screen.getByText(/Usa el formato EA-AAAA-NNN/)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(1);

    await usuario.clear(campo);
    await usuario.type(campo, 'ea-2026-001');
    await usuario.click(screen.getByRole('button', { name: 'Buscar' }));
    await screen.findByRole('cell', { name: 'GB-2026-0001' });
    expect(fetch.mock.calls.at(-1)[0]).toBe('/api/v1/alertas?zona=EA-2026-001&limite=10&desplazamiento=0');
  });

  it('indica cuando no hay resultados', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () => jsonResponse({ ...PAGINA, total: 0, alertas: [] })));
    renderizar();
    expect(await screen.findByText('No hay alertas que coincidan con los filtros.')).toBeInTheDocument();
  });
});
