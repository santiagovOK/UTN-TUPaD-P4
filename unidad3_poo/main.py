from figuras import (
    Taller, Lado, Etiqueta, Triangulo, Cuadrado, Pentagono, Hexagono,
    Poligono, exportar_todo
)
from libreria_externa import PlanoCAD
import weakref

def main():
    print("=== TPI UNIDAD 3: Demostración Ejecutable ===\n")

    # 1. FALLA TEMPRANA (ABC) - parte 3 y parte 5
    print("--- 1. Falla Temprana (Clase Abstracta) ---")
    try:
        # Prueba de instanciación de un Poligono puro, que hereda de ABC pero no implementa lados_esperados()
        p_invalido = Poligono("Falla", "Gris")
        print("ERROR: Esto no debería imprimir porque Poligono es abstracta.")
    except TypeError as e:
        print("Éxito: Se atrapó el TypeError al construir.")
        print(f"Mensaje de error: {e}\n")

    # 2. COMPOSICIÓN Y ETIQUETAS
    print("--- 2. Composición y Etiquetas ---")
    # Creamos etiquetas (0..1 Asociación)
    etq_base = Etiqueta("Base")
    etq_altura = Etiqueta("Altura")

    # Creamos el triángulo pasando los lados de forma anónima (inline).
    # La copia defensiva interna sella el ciclo de vida: el triángulo es el único dueño.
    triangulo = Triangulo("T1", "Rojo", [
        Lado(3.0, etq_base),
        Lado(4.0, etq_altura),
        Lado(5.0)
    ])
    
    print(f"Triángulo creado: {triangulo.nombre}")
    print("Sus lados fueron creados anónimamente dentro de la lista. Si el triángulo se destruye, los lados también (Composición).")
    
    # Se usa weakref para observar el lado sin crearle una referencia fuerte.
    # Si hiciéramos `ref = triangulo.lados[0]`, esa variable mantendría vivo al lado arruinando la prueba. El weakref permite que el Garbage Collector de Python lo destruya.
    lados_ref = weakref.ref(triangulo.lados[0])
    
    del triangulo
    print(f"¿Sobrevive el lado después de borrar el triángulo?: {'Sí' if lados_ref() else 'No'}\n")


    # 3. AGREGACIÓN E INVENTARIO (Taller - Polígono)
    print("--- 3. Agregación (Supervivencia del Polígono) ---")
    
    # Creamos un representante de cada subclase para tener al menos 4.
    # El cuadrado lo creamos manualmente para inyectar otra etiqueta (cumpliendo "etiquete al menos 2 lados")
    t2 = Triangulo.desde_medidas("T2", "Verde", 3, 3, 3)
    c1 = Cuadrado("C1", "Azul", [
        Lado(2.0, Etiqueta("Lado Superior")), 
        Lado(2.0), Lado(2.0), Lado(2.0)
    ])
    p1 = Pentagono.desde_medidas("P1", "Amarillo", 5, 5, 5, 5, 5)
    h1 = Hexagono.desde_medidas("H1", "Naranja", 6, 6, 6, 6, 6, 6)
    
    taller = Taller()
    taller.recibir(t2)
    taller.recibir(c1)
    taller.recibir(p1)
    taller.recibir(h1)

    print(f"Inventario del taller:")
    for pol in taller.inventario():
        print(f" - {pol.nombre} ({type(pol).__name__})")
    
    # Destruimos el taller
    del taller
    print("\nTaller destruido con 'del taller'.")
    
    # Comprobamos que el polígono sobrevive
    print(f"¿Sobrevive el cuadrado C1?: Sí, su nombre sigue siendo '{c1.nombre}'.\n")


    # 4. CONTRATOS ESTRUCTURALES Y DUCK TYPING (Exportable)
    print("--- 4. Duck Typing (Protocol Exportable) ---")
    
    # Rearmamos el inventario en una lista y le agregamos un PlanoCAD que no hereda de nada nuestro
    plano_externo = PlanoCAD("PL-001")
    
    elementos_exportables = [t2, c1, p1, h1, plano_externo]
    
    resultados_exportacion = exportar_todo(elementos_exportables)
    
    print("Resultados de la exportación conjunta:")
    for res in resultados_exportacion:
        print(f" - {res}")


if __name__ == "__main__":
    main()