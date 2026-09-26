export function ProductoForm() {
  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-6 mb-8">
      <h2 className="text-xl font-bold text-gray-900 mb-1">Registrar Nuevo Producto</h2>
      <p className="text-sm text-gray-500 mb-6">
        Formulario de alta con maquetado estático (componente funcional puro sin lógica de estado).
      </p>

      <form onSubmit={(e) => e.preventDefault()}>
        <fieldset className="space-y-4">
          <legend className="sr-only">Información del Producto</legend>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-1">
                Nombre del Producto
                <span aria-hidden="true" className="text-rose-600 ml-0.5">*</span>
                <span className="sr-only"> (obligatorio)</span>
              </label>
              <input
                id="nombre"
                type="text"
                name="nombre"
                required
                aria-required="true"
                defaultValue="Auriculares Inalámbricos Pro"
                placeholder="Ej: Teclado Mecánico"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-base md:text-sm"
              />
            </div>

            <div>
              <label htmlFor="precio" className="block text-sm font-medium text-gray-700 mb-1">
                Precio (ARS)
                <span aria-hidden="true" className="text-rose-600 ml-0.5">*</span>
                <span className="sr-only"> (obligatorio)</span>
              </label>
              <input
                id="precio"
                type="number"
                name="precio"
                required
                aria-required="true"
                defaultValue="45000"
                step="0.01"
                min="0"
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-base md:text-sm"
              />
            </div>
          </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="categoria" className="block text-sm font-medium text-gray-700 mb-1">
              Categoría
            </label>
            <input
              id="categoria"
              type="text"
              name="categoria"
              defaultValue="Audio"
              placeholder="Ej: Computación"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-base md:text-sm"
            />
          </div>

          <div>
            <label htmlFor="stock" className="block text-sm font-medium text-gray-700 mb-1">
              Stock Inicial
            </label>
            <input
              id="stock"
              type="number"
              name="stock"
              defaultValue="25"
              min="0"
              placeholder="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-base md:text-sm"
            />
          </div>
        </div>

        <div>
          <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-1">
            Descripción
          </label>
          <textarea
            id="descripcion"
            name="descripcion"
            rows={3}
            defaultValue="Cancelación activa de ruido con batería de hasta 30 horas continuas y carga rápida."
            placeholder="Descripción detallada del producto..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-base md:text-sm"
          />
        </div>
        </fieldset>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="w-full sm:w-auto px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer"
          >
            Guardar Producto
          </button>
        </div>
      </form>
    </section>
  );
}

export default ProductoForm;
