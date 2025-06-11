from estudiantes import agregar_estudiante, listar_estudiantes
from asistencia import registrar_asistencia, consultar_asistencia
from utils import mostrar_menu

def main():
    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            agregar_estudiante()
        elif opcion == "2":
            listar_estudiantes()
        elif opcion == "3":
            registrar_asistencia()
        elif opcion == "4":
            consultar_asistencia()
        elif opcion == "5":
            print("Saliendo del sistema.")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main()

def mostrar_menu():
    print("\n--- Sistema de Gestión de Asistencia ---")
    print("1. Agregar estudiante")
    print("2. Listar estudiantes")
    print("3. Registrar asistencia")
    print("4. Consultar asistencia")
    print("5. Salir")
    return input("Seleccione una opción: ")
