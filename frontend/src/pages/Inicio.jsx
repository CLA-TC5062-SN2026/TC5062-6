export default function Inicio() {
  return (
    <main className="min-h-screen bg-slate-50 px-5 py-12 sm:py-20">
      <section className="mx-auto max-w-3xl rounded-2xl border border-emerald-100 bg-white p-7 shadow-sm sm:p-12">
        <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-emerald-700">
          EcoAlert Tambopata
        </p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
          Frontend inicial configurado
        </h1>
        <p className="mt-5 max-w-2xl text-base leading-7 text-slate-700">
          Proyecto creado con React, Vite y Tailwind CSS. Esta pantalla
          comprueba el arranque y la configuración básica de estilos.
        </p>
        <p className="mt-7 rounded-lg bg-emerald-50 p-4 text-sm font-medium text-emerald-900">
          Parte 1: scaffolding básico. Los componentes reutilizables se
          implementarán en la Parte 2.
        </p>
      </section>
    </main>
  );
}
