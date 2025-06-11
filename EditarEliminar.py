import sqlite3

DATABASE_NAME = "registro_asistencia.db"

class DatabaseManager:
    def __init__(self, db_name=DATABASE_NAME):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self):
        """Obtiene una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row # Para acceder a las columnas por nombre
        return conn

    def _create_table(self):
        """Crea la tabla 'individuos' si no existe."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS individuos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                dni TEXT UNIQUE NOT NULL,
                fecha_nacimiento TEXT, -- YYYY-MM-DD
                genero TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print(f"Tabla 'individuos' asegurada en {self.db_name}")

    # --- Funciones para la tarea de "Alta de Individuo" (para tu compañero) ---
    def add_individuo(self, nombre, apellido, dni, fecha_nacimiento=None, genero=None):
        """Agrega un nuevo individuo a la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO individuos (nombre, apellido, dni, fecha_nacimiento, genero)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, apellido, dni, fecha_nacimiento, genero))
            conn.commit()
            print(f"Individuo '{nombre} {apellido}' (DNI: {dni}) agregado exitosamente.")
            return cursor.lastrowid # Retorna el ID del nuevo individuo
        except sqlite3.IntegrityError:
            print(f"Error: Ya existe un individuo con el DNI '{dni}'.")
            return None
        except Exception as e:
            print(f"Error al agregar individuo: {e}")
            return None
        finally:
            conn.close()

    # --- Funciones para la tarea de "Edición y Eliminación de Individuos" (TU TAREA) ---
    def update_individuo(self, individuo_id, nombre=None, apellido=None, dni=None, fecha_nacimiento=None, genero=None):
        """Actualiza los datos de un individuo existente."""
        conn = self._get_connection()
        cursor = conn.cursor()
        set_clauses = []
        params = []

        if nombre:
            set_clauses.append("nombre = ?")
            params.append(nombre)
        if apellido:
            set_clauses.append("apellido = ?")
            params.append(apellido)
        if dni:
            # Si se actualiza el DNI, debe ser único
            set_clauses.append("dni = ?")
            params.append(dni)
        if fecha_nacimiento:
            set_clauses.append("fecha_nacimiento = ?")
            params.append(fecha_nacimiento)
        if genero:
            set_clauses.append("genero = ?")
            params.append(genero)

        if not set_clauses:
            print("No se proporcionaron datos para actualizar.")
            return False

        params.append(individuo_id)
        query = f"UPDATE individuos SET {', '.join(set_clauses)} WHERE id = ?"

        try:
            cursor.execute(query, tuple(params))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Individuo con ID {individuo_id} actualizado exitosamente.")
                return True
            else:
                print(f"No se encontró un individuo con ID {individuo_id}.")
                return False
        except sqlite3.IntegrityError:
            print(f"Error: El DNI '{dni}' ya está en uso por otro individuo.")
            return False
        except Exception as e:
            print(f"Error al actualizar individuo con ID {individuo_id}: {e}")
            return False
        finally:
            conn.close()

    def delete_individuo(self, individuo_id):
        """Elimina un individuo de la base de datos por su ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # OPCIONAL: Antes de eliminar, podrías verificar si hay asistencias
            # relacionadas y decidir qué hacer (eliminar en cascada, anular, etc.)
            # Por simplicidad, aquí solo eliminamos el individuo.
            # Una tabla de asistencias podría tener una clave foránea que maneje esto.

            cursor.execute("DELETE FROM individuos WHERE id = ?", (individuo_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Individuo con ID {individuo_id} eliminado exitosamente.")
                return True
            else:
                print(f"No se encontró un individuo con ID {individuo_id}.")
                return False
        except Exception as e:
            print(f"Error al eliminar individuo con ID {individuo_id}: {e}")
            return False
        finally:
            conn.close()

    # --- Funciones para la tarea de "Registro de Asistencia" y "Filtros" ---
    def get_individuo_by_id(self, individuo_id):
        """Obtiene un individuo por su ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM individuos WHERE id = ?", (individuo_id,))
        individuo = cursor.fetchone()
        conn.close()
        return dict(individuo) if individuo else None

    def get_individuo_by_dni(self, dni):
        """Obtiene un individuo por su DNI."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM individuos WHERE dni = ?", (dni,))
        individuo = cursor.fetchone()
        conn.close()
        return dict(individuo) if individuo else None

    def get_all_individuos(self):
        """Obtiene todos los individuos registrados."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM individuos ORDER BY apellido, nombre")
        individuos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return individuos

    def get_individuos_by_criteria(self, **kwargs):
        """
        Obtiene individuos basados en criterios de búsqueda (para el compañero de filtros).
        Ejemplo: get_individuos_by_criteria(genero='Masculino', nombre='Juan')
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM individuos WHERE 1=1"
        params = []
        for key, value in kwargs.items():
            if key in ['nombre', 'apellido', 'dni', 'fecha_nacimiento', 'genero']:
                query += f" AND {key} LIKE ?"
                params.append(f"%{value}%") # Permite búsqueda parcial

        query += " ORDER BY apellido, nombre"
        cursor.execute(query, tuple(params))
        individuos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return individuos


if __name__ == "__main__":
    # Este bloque solo se ejecuta si corres database_manager.py directamente
    # Útil para pruebas iniciales o configuración de la DB
    db_manager = DatabaseManager()

    print("\n--- Probando la creación/actualización de tabla ---")
    db_manager._create_table()

    print("\n--- Probando la adición de individuos (tarea del otro compañero) ---")
    db_manager.add_individuo("Alice", "Smith", "12345678", "2000-01-15", "Femenino")
    db_manager.add_individuo("Bob", "Johnson", "87654321", "1995-05-20", "Masculino")
    db_manager.add_individuo("Charlie", "Brown", "11223344", "2002-11-01", "Masculino")
    db_manager.add_individuo("Alice", "Smith", "12345678", "2000-01-15", "Femenino") # DNI duplicado

    print("\n--- Listando todos los individuos ---")
    all_individuos = db_manager.get_all_individuos()
    for ind in all_individuos:
        print(f"ID: {ind['id']}, Nombre: {ind['nombre']} {ind['apellido']}, DNI: {ind['dni']}")

    print("\n--- Probando la edición de un individuo (TU TAREA) ---")
    # Asumimos que Alice Smith tiene ID 1 (si fue la primera insertada)
    # Primero buscamos a Alice por DNI para obtener su ID
    alice = db_manager.get_individuo_by_dni("12345678")
    if alice:
        print(f"Editando a: {alice['nombre']} {alice['apellido']} (ID: {alice['id']})")
        db_manager.update_individuo(alice['id'], nombre="Alicia", fecha_nacimiento="2000-01-16")
        updated_alice = db_manager.get_individuo_by_id(alice['id'])
        print(f"Después de editar: {updated_alice}")
    else:
        print("Alice no encontrada para editar.")

    print("\n--- Intentando editar con DNI duplicado ---")
    bob = db_manager.get_individuo_by_dni("87654321")
    if bob:
        db_manager.update_individuo(bob['id'], dni="11223344") # Intentando usar el DNI de Charlie
    else:
        print("Bob no encontrado para prueba de DNI duplicado.")


    print("\n--- Listando individuos después de la edición ---")
    all_individuos = db_manager.get_all_individuos()
    for ind in all_individuos:
        print(f"ID: {ind['id']}, Nombre: {ind['nombre']} {ind['apellido']}, DNI: {ind['dni']}")

    print("\n--- Probando la eliminación de un individuo (TU TAREA) ---")
    # Intentar eliminar a Charlie Brown
    charlie = db_manager.get_individuo_by_dni("11223344")
    if charlie:
        print(f"Eliminando a: {charlie['nombre']} {charlie['apellido']} (ID: {charlie['id']})")
        db_manager.delete_individuo(charlie['id'])
    else:
        print("Charlie no encontrado para eliminar.")

    print("\n--- Listando individuos después de la eliminación ---")
    all_individuos = db_manager.get_all_individuos()
    for ind in all_individuos:
        print(f"ID: {ind['id']}, Nombre: {ind['nombre']} {ind['apellido']}, DNI: {ind['dni']}")

    print("\n--- Probando filtros (para el compañero de filtros) ---")
    hombres = db_manager.get_individuos_by_criteria(genero='Masculino')
    print("Hombres en la base de datos:")
    for ind in hombres:
        print(f"  - {ind['nombre']} {ind['apellido']}")

    nombre_parcial = db_manager.get_individuos_by_criteria(nombre='ali')
    print("Individuos con 'ali' en el nombre:")
    for ind in nombre_parcial:
        print(f"  - {ind['nombre']} {ind['apellido']}")
        
        from database_manager import DatabaseManager

def display_menu():
    print("\n--- Sistema de Registro de Asistencia ---")
    print("1. Agregar Individuo (para compañero de Alta)")
    print("2. Ver Todos los Individuos")
    print("3. Editar Individuo (TU TAREA)")
    print("4. Eliminar Individuo (TU TAREA)")
    print("5. Buscar Individuos por Criterio (para compañero de Filtros)")
    print("6. Registrar Asistencia (para compañero de Asistencia)")
    print("0. Salir")
    print("-----------------------------------------")

def run_system():
    db_manager = DatabaseManager()

    while True:
        display_menu()
        choice = input("Selecciona una opción: ")

        if choice == '1':
            # Funcionalidad de 'Alta de Individuo' (simulada)
            print("\n--- Agregando Individuo ---")
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            dni = input("DNI: ")
            fecha_nacimiento = input("Fecha de Nacimiento (YYYY-MM-DD, opcional): ")
            genero = input("Género (opcional): ")
            db_manager.add_individuo(nombre, apellido, dni, fecha_nacimiento if fecha_nacimiento else None, genero if genero else None)

        elif choice == '2':
            # Funcionalidad general para ver individuos
            print("\n--- Lista de Individuos ---")
            individuos = db_manager.get_all_individuos()
            if not individuos:
                print("No hay individuos registrados.")
            else:
                for ind in individuos:
                    print(f"ID: {ind['id']}, Nombre: {ind['nombre']} {ind['apellido']}, DNI: {ind['dni']}, Fecha Nac: {ind['fecha_nacimiento']}, Género: {ind['genero']}")

        elif choice == '3':
            # --- TU TAREA: Edición de Individuo ---
            print("\n--- Editando Individuo ---")
            individuo_id = input("Introduce el ID del individuo a editar: ")
            try:
                individuo_id = int(individuo_id)
            except ValueError:
                print("ID inválido. Debe ser un número.")
                continue

            individuo = db_manager.get_individuo_by_id(individuo_id)
            if not individuo:
                print(f"No se encontró ningún individuo con ID {individuo_id}.")
                continue

            print(f"Editando a: {individuo['nombre']} {individuo['apellido']} (DNI: {individuo['dni']})")
            print("Deja el campo vacío si no quieres modificarlo.")

            new_nombre = input(f"Nuevo Nombre ({individuo['nombre']}): ") or None
            new_apellido = input(f"Nuevo Apellido ({individuo['apellido']}): ") or None
            new_dni = input(f"Nuevo DNI ({individuo['dni']}): ") or None
            new_fecha_nacimiento = input(f"Nueva Fecha de Nacimiento ({individuo['fecha_nacimiento']}): ") or None
            new_genero = input(f"Nuevo Género ({individuo['genero']}): ") or None

            db_manager.update_individuo(
                individuo_id,
                nombre=new_nombre,
                apellido=new_apellido,
                dni=new_dni,
                fecha_nacimiento=new_fecha_nacimiento,
                genero=new_genero
            )

        elif choice == '4':
            # --- TU TAREA: Eliminación de Individuo ---
            print("\n--- Eliminando Individuo ---")
            individuo_id = input("Introduce el ID del individuo a eliminar: ")
            try:
                individuo_id = int(individuo_id)
            except ValueError:
                print("ID inválido. Debe ser un número.")
                continue

            individuo = db_manager.get_individuo_by_id(individuo_id)
            if not individuo:
                print(f"No se encontró ningún individuo con ID {individuo_id}.")
                continue

            confirm = input(f"¿Estás seguro de que quieres eliminar a {individuo['nombre']} {individuo['apellido']} (ID: {individuo_id})? (s/n): ").lower()
            if confirm == 's':
                db_manager.delete_individuo(individuo_id)
            else:
                print("Eliminación cancelada.")

        elif choice == '5':
            # Funcionalidad de 'Filtros' (simulada)
            print("\n--- Buscando Individuos por Criterio ---")
            print("Deja un campo vacío si no quieres usarlo como filtro.")
            filtro_nombre = input("Filtrar por Nombre: ") or None
            filtro_apellido = input("Filtrar por Apellido: ") or None
            filtro_dni = input("Filtrar por DNI: ") or None
            filtro_genero = input("Filtrar por Género: ") or None

            search_criteria = {}
            if filtro_nombre: search_criteria['nombre'] = filtro_nombre
            if filtro_apellido: search_criteria['apellido'] = filtro_apellido
            if filtro_dni: search_criteria['dni'] = filtro_dni
            if filtro_genero: search_criteria['genero'] = filtro_genero

            if not search_criteria:
                print("No se especificó ningún criterio de búsqueda.")
                continue

            resultados = db_manager.get_individuos_by_criteria(**search_criteria)
            if not resultados:
                print("No se encontraron individuos con esos criterios.")
            else:
                print("\nResultados de la búsqueda:")
                for ind in resultados:
                    print(f"ID: {ind['id']}, Nombre: {ind['nombre']} {ind['apellido']}, DNI: {ind['dni']}")

        elif choice == '6':
            # Funcionalidad de 'Registro de Asistencia' (simulada)
            print("\n--- Registrando Asistencia (PENDIENTE DE IMPLEMENTACIÓN DE COMPAÑERO) ---")
            print("Esta función debería permitir registrar la asistencia de un individuo.")
            # Aquí tu compañero de asistencia podría usar db_manager.get_individuo_by_dni()
            # o db_manager.get_individuo_by_id() para verificar al individuo antes de registrar.
            # También podría necesitar una tabla separada para 'asistencias'.

        elif choice == '0':
            print("Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")

if __name__ == "__main__":
    run_system()
    
    