import { useState, useEffect, useCallback } from 'react';
import type { Categoria } from './types/categoria';
import { Navbar } from './components/Navbar';
import { CategoriaModal } from './components/CategoriaModal';
import { CategoriaList } from './components/CategoriaList';
import { Footer } from './components/Footer';

export function App() {
  // [Consigna TP6 - Parte B, inciso e]: useState para la lista de categorías, estado del modal y categoría en edición.
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [categoriaEnEdicion, setCategoriaEnEdicion] = useState<Categoria | null>(null);
  // [Consigna TP6 - Parte B, inciso e]: Manejo de estado de carga (loading) y error en la UI.
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // [Consigna TP6 - Parte B, inciso e]: useEffect para cargar las categorías al montar el componente (GET /categorias) con fetch nativo y AbortController.
  const fetchCategorias = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/categorias/', { signal });
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      const data: Categoria[] = await response.json();
      setCategorias(data);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Petición cancelada intencionalmente al desmontar o re-ejecutar el efecto
        return;
      }
      const detalle = err instanceof Error ? err.message : 'Error de conexión';
      setError(`No se pudieron cargar las categorías: ${detalle}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const abortController = new AbortController();
    fetchCategorias(abortController.signal);

    return () => {
      abortController.abort();
    };
  }, [fetchCategorias]);

  const handleOpenCreateModal = () => {
    setCategoriaEnEdicion(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (categoria: Categoria) => {
    setCategoriaEnEdicion(categoria);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setCategoriaEnEdicion(null);
  };

  // [Consigna TP6 - Parte B, inciso e]: Funciones de mutación CRUD con fetch nativo — handleCreate (POST) y handleUpdate (PUT) con actualización inmutable del estado.
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);
    const nombre = (formData.get('nombre') as string)?.trim();
    const descripcion = (formData.get('descripcion') as string)?.trim() || null;

    if (!nombre) {
      setError('El nombre de la categoría es obligatorio');
      return;
    }

    const payload = {
      nombre,
      descripcion,
      activo: categoriaEnEdicion ? categoriaEnEdicion.activo : true,
    };

    setLoading(true);
    setError(null);

    try {
      if (categoriaEnEdicion) {
        const response = await fetch(
          `http://localhost:8000/categorias/${categoriaEnEdicion.id}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          }
        );

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const updatedCategoria: Categoria = await response.json();
        setCategorias((prev) =>
          prev.map((c) => (c.id === updatedCategoria.id ? updatedCategoria : c))
        );
        handleCloseModal();
      } else {
        const response = await fetch('http://localhost:8000/categorias/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const newCategoria: Categoria = await response.json();
        setCategorias((prev) => [...prev, newCategoria]);
        handleCloseModal();
      }
    } catch (err) {
      const detalle = err instanceof Error ? err.message : 'Error de conexión';
      setError(`No se pudo guardar la categoría: ${detalle}`);
    } finally {
      setLoading(false);
    }
  };

  // [Consigna TP6 - Parte B, inciso e]: Función handleDelete (DELETE) con confirmación previa y eliminación inmutable del estado.
  const handleDelete = async (id: number) => {
    const confirmacion = window.confirm(
      '¿Estás seguro de que deseas eliminar esta categoría?'
    );
    if (!confirmacion) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/categorias/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      setCategorias((prev) => prev.filter((c) => c.id !== id));
      if (categoriaEnEdicion?.id === id) {
        handleCloseModal();
      }
    } catch (err) {
      const detalle = err instanceof Error ? err.message : 'Error de conexión';
      setError(`No se pudo eliminar la categoría: ${detalle}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col">
      {/* Skip Link para accesibilidad de teclado */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-3 focus:left-3 focus:px-4 focus:py-2 focus:bg-indigo-600 focus:text-white focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 font-medium text-sm transition-all"
      >
        Saltar al contenido principal
      </a>

      <Navbar />

      <main
        id="main-content"
        className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8"
      >
        <h1 className="sr-only">Gestor de Categorías - Panel Principal</h1>

        {error && (
          <div
            role="alert"
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center justify-between gap-4"
          >
            <span>{error}</span>
            <button
              type="button"
              onClick={() => void fetchCategorias()}
              className="px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-800 font-medium text-xs rounded-md transition-colors cursor-pointer shrink-0 focus:outline-none focus:ring-2 focus:ring-red-400"
            >
              Reintentar
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-start">
          <div className="lg:col-span-1">
            {isModalOpen ? (
              <CategoriaModal
                // [Consigna TP6 - Parte B, inciso e]: Pasar las funciones y el estado como props a los componentes hijos.
                key={categoriaEnEdicion?.id ?? 'new'}
                isOpen={isModalOpen}
                categoriaAEditar={categoriaEnEdicion}
                onClose={handleCloseModal}
                onSubmit={handleSubmit}
                isSubmitting={loading}
              />
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col items-center justify-center text-center gap-3">
                <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center">
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                </div>
                <div>
                  <h2 className="text-base font-semibold text-gray-900">
                    Gestión de Categorías
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Crea una nueva categoría para organizar los productos del catálogo.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleOpenCreateModal}
                  className="mt-2 w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Registrar Nueva Categoría
                </button>
              </div>
            )}
          </div>
          <div className="lg:col-span-2">
            {loading ? (
              <div
                role="status"
                aria-live="polite"
                className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300"
              >
                <p className="text-gray-500 text-base">Cargando categorías...</p>
              </div>
            ) : (
              <CategoriaList
                // [Consigna TP6 - Parte B, inciso e]: Pasar las funciones y el estado como props a los componentes hijos.
                categorias={categorias}
                onEdit={handleOpenEditModal}
                onDelete={handleDelete}
              />
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
