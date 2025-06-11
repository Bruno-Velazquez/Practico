import sqlite3
from datetime import datetime

# --- Configuración inicial de la base de datos (puede ir en otro archivo) ---
DB_NAME = "asistencia.db"

def conectar():
    return sqlite3.connect(DB_NAME)

# --- Crear tabla si no existe ---
def crear_tablas():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asistencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                fecha TEXT,
                estado TEXT,
                UNIQUE(usuario_id, fecha)
            )
        ''')
        conn.commit()

# --- Obtener lista de usuarios activos (filtrado por rol o curso, simplificado) ---
def obtener_usuarios_activos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM usuarios WHERE estado = 'Activo'")
        return cursor.fetchall()

# --- Registrar o actualizar asistencia ---
def marcar_asistencia(usuario_id, fecha, estado):
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO asistencia (usuario_id, fecha, estado)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario_id, fecha) DO UPDATE SET estado = excluded.estado
            ''', (usuario_id, fecha, estado))
            conn.commit()
        except Exception as e:
            print(f"Error al guardar la asistencia: {e}")

# --- Interfaz simple de consola ---
def registrar_asistencia():
    crear_tablas()
    usuarios = obtener_usuarios_activos()
    if not usuarios:
        print("No hay usuarios activos registrados.")
        return

    fecha = input(f"Ingrese la fecha (YYYY-MM-DD) [Por defecto: hoy {datetime.today().date()}]: ").strip()
    if not fecha:
        fecha = str(datetime.today().date())

    print("\nOpciones de asistencia: [P]resente | [A]usente | [T]arde | [J]ustificado")
    for usuario in usuarios:
        usuario_id, nombre = usuario
        estado = input(f"{nombre}: ").strip().upper()
        estados_validos = {'P': 'Presente', 'A': 'Ausente', 'T': 'Tarde', 'J': 'Justificado'}

        if estado not in estados_validos:
            print("Estado no válido. Se marcará como 'Ausente' por defecto.")
            estado = 'A'

        marcar_asistencia(usuario_id, fecha, estados_validos[estado])

    print("\n✅ Asistencia registrada con éxito.")

# --- Ejecutar el flujo principal ---
if __name__ == "__main__":
    registrar_asistencia()
