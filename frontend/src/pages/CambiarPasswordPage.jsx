// Cambio de contraseña (RF-02-AC-4): una cuenta creada con contraseña temporal debe definir una propia
// antes de usar el sistema (el backend responde 403 CAMBIO_PASSWORD_REQUERIDO mientras tanto).
// PUT /auth/password mantiene esta sesión y cierra las demás de la cuenta.

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button.jsx';
import Card from '../components/Card.jsx';
import ErrorAlert from '../components/ErrorAlert.jsx';
import Input from '../components/Input.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { authService } from '../services/authService.js';

const MIN_PASSWORD = 12; // PS-15
const MAX_PASSWORD = 128;
const VACIO = { actual: '', nueva: '', confirmacion: '' };

function validar({ actual, nueva, confirmacion }) {
  const errores = {};
  if (!actual) errores.actual = 'Ingresa tu contraseña actual.';
  if (nueva.length < MIN_PASSWORD) errores.nueva = `Debe tener al menos ${MIN_PASSWORD} caracteres.`;
  else if (nueva.length > MAX_PASSWORD) errores.nueva = `Admite como máximo ${MAX_PASSWORD} caracteres.`;
  else if (nueva === actual) errores.nueva = 'Debe ser distinta de la contraseña actual.';
  if (confirmacion !== nueva) errores.confirmacion = 'Las contraseñas no coinciden.';
  return errores;
}

export default function CambiarPasswordPage() {
  const { usuario, refrescarUsuario } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(VACIO);
  const [errores, setErrores] = useState({});
  const [errorServidor, setErrorServidor] = useState(null);
  const [enviando, setEnviando] = useState(false);

  function actualizar(campo) {
    return (event) => setForm((previo) => ({ ...previo, [campo]: event.target.value }));
  }

  async function enviar(event) {
    event.preventDefault();
    const encontrados = validar(form);
    setErrores(encontrados);
    setErrorServidor(null);
    if (Object.keys(encontrados).length > 0) return;

    setEnviando(true);
    try {
      await authService.cambiarPassword({ actual: form.actual, nueva: form.nueva });
      await refrescarUsuario();
      navigate('/dashboard', { replace: true });
    } catch (error) {
      setErrorServidor(error.message);
      setForm(VACIO);
      setEnviando(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-2 text-3xl font-bold text-green-800">Cambiar contraseña</h1>
      <p className="mb-6 text-gray-600">
        {usuario?.debe_cambiar_password
          ? 'Tu cuenta tiene una contraseña temporal. Define una propia para continuar.'
          : 'Al cambiarla se cerrarán tus sesiones abiertas en otros navegadores.'}
      </p>
      <Card>
        <form noValidate onSubmit={enviar} className="flex flex-col gap-4">
          <ErrorAlert titulo="No se pudo cambiar la contraseña" mensaje={errorServidor} />
          <Input
            label="Contraseña actual"
            type="password"
            autoComplete="current-password"
            value={form.actual}
            onChange={actualizar('actual')}
            error={errores.actual}
          />
          <Input
            label="Contraseña nueva"
            type="password"
            autoComplete="new-password"
            value={form.nueva}
            onChange={actualizar('nueva')}
            error={errores.nueva}
            maxLength={MAX_PASSWORD}
          />
          <Input
            label="Repite la contraseña nueva"
            type="password"
            autoComplete="new-password"
            value={form.confirmacion}
            onChange={actualizar('confirmacion')}
            error={errores.confirmacion}
            maxLength={MAX_PASSWORD}
          />
          <Button type="submit" loading={enviando}>
            Guardar contraseña
          </Button>
        </form>
      </Card>
    </div>
  );
}
