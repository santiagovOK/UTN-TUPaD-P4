from assets.parte1_diagnostico import Poligono, Lado

def demo_getter_setter_bypass():
    print("--- Demostrando Javismo #1: Getters/Setters (Bypass de validación) ---")
    # Al depender de un setter estilo Java para validar, es común que el __init__ 
    # asigne directamente a la variable "privada" (_longitud), evadiendo la regla.
    l_invalido = Lado(-10)
    print(f"Lado instanciado con longitud: {l_invalido.getLongitud()}")
    print("El lado se creó con longitud negativa. La validación fue evadida.\n")

def demo_type_hint_enganioso():
    print("--- Demostrando Javismo #7: Type hints engañosos ---")
    p = Poligono("P", "verde")
    resultado = p.area()
    
    print(f"El método area() indica en su firma que devuelve un 'int'.")
    print(f"Valor real devuelto: '{resultado}' (Tipo real: {type(resultado).__name__})")
    print("Intentando sumar 10 al área confiando ciegamente en el type hint...")
    
    try:
        total = resultado + 10
    except TypeError as e:
        print("Atrapado TypeError en runtime:", e)

if __name__ == "__main__":
    demo_getter_setter_bypass()
    demo_type_hint_enganioso()
