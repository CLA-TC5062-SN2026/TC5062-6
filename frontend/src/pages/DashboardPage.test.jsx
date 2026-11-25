import { render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AppRoutes } from '../App.jsx';
import { AuthProvider } from '../context/AuthContext.jsx';
import { tokenStorage } from '../services/tokenStorage.js';
import { USUARIO, jsonResponse } from '../test/respuestas.js';
import { resumirAlertas } from './DashboardPage.jsx';

function alerta(codigo, zona, area, fecha, presente = true) {
  return {
    id: `id-${codigo}`,
    fuente: 'GeoBosques',
    codigo,
    fecha_deteccion: fecha,
    fecha_ingesta: '2026-10-29T09:00:00Z',
    presente_en_ultima_carga: presente,
    zona_codigo: zona,
    area_ha: area,
  };
}

const ALERTAS = [
  alerta('GB-2026-0001', 'EA-2026-101', 3.1, '2026-10-25'),
  alerta('GB-2026-0004', 'EA-2026-101', 3.1, '2026-10-16', false),
  alerta('GB-2026-0005', 'EA-2026-102', 2.04, '2026-10-13'),
];

const CARGA = {
  id: '30000000-0000-4000-8000-000000000001',
  fuente: 'GeoBosques',
  fecha_corte: '2026-10-28',
  cargada_en: '2026-10-28T15:00:00Z',
  cargada_por: { id: USUARIO.id, nombre_completo: 'Carmen Mamani Ccori' },
};

function renderizarPanel(rutas) {
  tokenStorage.guardar('jwt', 3600);
  const fetchMock = vi.fn().mockImplementation(async (url) => {
    const ruta = new URL(url, 'http://localhost').pathname.replace('/api/v1', '');
    if (ruta === '/auth/me') return jsonResponse({ usuario: rutas.usuario ?? USUARIO, ultima_actividad: 'x' });
    if (ruta === '/alertas') return jsonResponse(rutas.alertas);
    if (ruta === '/cargas-alertas') return jsonResponse(rutas.cargas ?? []);
    throw new Error(`Ruta no simulada: ${ruta}`);
  });
  vi.stubGlobal('fetch', fetchMock);
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  );
  return fetchMock;
}

describe('resumirAlertas', () => {
  it('agrupa por zona, suma superficies, cuenta ausentes y ordena de mayor a menor superficie', () => {
    const { ausentes, superficie, zonas } = resumirAlertas(ALERTAS);
    expect(ausentes).toBe(1);
    expect(superficie).toBeCloseTo(8.24);
    expect(zonas.map((z) => [z.codigo, z.alertas, Number(z.superficie.toFixed(2)), z.ultimaDeteccion])).toEqual([
      ['EA-2026-101', 2, 6.2, '2026-10-25'],
      ['EA-2026-102', 1, 2.04, '2026-10-13'],
    ]);
  });
});

describe('DashboardPage', () => {
  it('muestra las cifras, la última carga y las zonas calculadas con /alertas y /cargas-alertas', async () => {
    const fetchMock = renderizarPanel({ alertas: { total: 3, limite: 500, desplazamiento: 0, alertas: ALERTAS }, cargas: [CARGA] });

    const tabla = await screen.findByRole('table', { name: 'Zonas de cambio ordenadas por superficie alertada' });
    const cifras = screen.getByText('Alertas cargadas').closest('dl');
    expect(within(cifras).getByText('3')).toBeInTheDocument();
    expect(within(cifras).getByText('8.24')).toBeInTheDocument();
    expect(screen.getByText(/Carmen Mamani Ccori/)).toBeInTheDocument();

    const filas = within(tabla).getAllByRole('row').slice(1);
    expect(within(filas[0]).getByRole('link', { name: 'EA-2026-101' })).toHaveAttribute('href', '/alertas?zona=EA-2026-101');
    expect(within(filas[0]).getByText('6.20')).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => url === '/api/v1/alertas?limite=500&desplazamiento=0')).toBe(true);
  });

  it('avisa cuando el resumen no incluye todas las alertas', async () => {
    renderizarPanel({ alertas: { total: 900, limite: 500, desplazamiento: 0, alertas: ALERTAS } });
    expect(await screen.findByText('El resumen usa las 3 alertas más recientes de 900.')).toBeInTheDocument();
  });

  it('con contraseña temporal no consulta datos: solo pide cambiarla', async () => {
    const fetchMock = renderizarPanel({ usuario: { ...USUARIO, debe_cambiar_password: true } });
    expect(await screen.findByRole('link', { name: 'Cambiar mi contraseña' })).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => url.includes('/alertas'))).toBe(false);
  });
});
