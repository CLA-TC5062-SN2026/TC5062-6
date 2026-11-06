
import { useState } from "react";

import Button from "./components/Button";
import Input from "./components/Input";
import Card from "./components/Card";
import Navbar from "./components/Navbar";

export default function App() {
  // Estado simulado de autenticación
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Estado del campo de búsqueda
  const [zona, setZona] = useState("");

  // Estado para demostrar la validación visual
  const [error, setError] = useState("");

  // Estado para demostrar el botón en carga
  const [loading, setLoading] = useState(false);

  function consultarZona() {
    if (!zona.trim()) {
      setError("Debes ingresar una zona de monitoreo.");
      return;
    }

    setError("");
    setLoading(true);

    // Simula una consulta sin conectar todavía el backend
    setTimeout(() => {
      setLoading(false);
    }, 1500);
  }

  function limpiarFormulario() {
    setZona("");
    setError("");
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar
        isAuthenticated={isAuthenticated}
        userName="Usuario de prueba"
        onLogin={() => setIsAuthenticated(true)}
        onLogout={() => setIsAuthenticated(false)}
      />

      <main className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-green-800 mb-2">
          Panel de monitoreo ambiental
        </h1>

        <p className="text-gray-600 mb-8">
          Demostración de componentes reutilizables
          de EcoAlert Tambopata.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Consulta de zonas" headingLevel={2}>
            <div className="flex flex-col gap-4">
              <Input
                label="Zona de monitoreo"
                value={zona}
                onChange={(event) => setZona(event.target.value)}
                placeholder="Ej. Tambopata"
                error={error}
              />

              <div className="flex flex-wrap gap-3">
                <Button
                  variant="primary"
                  loading={loading}
                  onClick={consultarZona}
                >
                  Consultar
                </Button>

                <Button
                  variant="secondary"
                  onClick={limpiarFormulario}
                >
                  Limpiar
                </Button>
              </div>
            </div>
          </Card>

          <Card
            title="Estado del monitoreo"
            footer="Información demostrativa, sin conexión al backend."
            headingLevel={2}
          >
            <p className="mb-2">
              <strong>Región:</strong> Tambopata
            </p>

            <p className="mb-2">
              <strong>Tipo:</strong> Monitoreo ambiental
            </p>

            <p>
              <strong>Estado:</strong> En observación
            </p>
          </Card>
        </div>

        <div className="mt-6">
          <Card title="Prueba de estado de carga" headingLevel={2}>
            <p className="mb-4">
              Este botón muestra permanentemente el estado
              de carga para verificar su presentación.
            </p>

            <Button loading={true}>
              Procesar información
            </Button>
          </Card>
        </div>
      </main>
    </div>
  );
}
