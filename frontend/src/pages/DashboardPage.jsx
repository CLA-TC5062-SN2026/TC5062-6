// Panel principal tras iniciar sesión (ruta protegida).

import { Link } from 'react-router-dom';
import Card from '../components/Card.jsx';
import { useAuth } from '../context/AuthContext.jsx';

const ROLES = {
  analista_sig: 'Analista SIG',
  coordinacion: 'Coordinación',
};

export default function DashboardPage() {
  const { usuario } = useAuth();

  return (
    <>
      <h1 className="mb-2 text-3xl font-bold text-green-800">Panel de monitoreo ambiental</h1>
      <p className="mb-8 text-gray-600">
        Bienvenido(a), {usuario.nombre_completo}. Estás en una ruta protegida: solo es visible con una sesión válida.
      </p>

      {usuario.debe_cambiar_password && (
        <div role="alert" className="mb-6 rounded-md border border-amber-300 bg-amber-50 p-4 text-amber-900">
          Tu cuenta tiene una contraseña temporal. Debes cambiarla antes de consultar la información del sistema.
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <Card title="Tu sesión" headingLevel={2}>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2">
            <dt className="font-semibold">Correo</dt>
            <dd className="break-all">{usuario.correo}</dd>
            <dt className="font-semibold">Rol</dt>
            <dd>{ROLES[usuario.rol] ?? usuario.rol}</dd>
          </dl>
        </Card>

        <Card title="Alertas de deforestación" headingLevel={2}>
          <p className="mb-4">Consulta las alertas de GeoBosques ingeridas y la zona a la que pertenecen.</p>
          <Link
            to="/alertas"
            className="inline-flex rounded-md bg-green-700 px-4 py-2 font-medium text-white hover:bg-green-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-800"
          >
            Ver alertas
          </Link>
        </Card>
      </div>
    </>
  );
}
