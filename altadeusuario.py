from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'  # Usa SQLite para simplicidad
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # Alumno, Profesor, Administrador
    estado = db.Column(db.String(10), default='Activo')

    def __repr__(self):
        return f'<Usuario {self.nombre_completo}>'

# Crear la base de datos
with app.app_context():
    db.create_all()

# Ruta para registrar un nuevo usuario
@app.route('/usuarios', methods=['POST'])
def registrar_usuario():
    data = request.get_json()

    # Validación básica
    required_fields = ['nombre_completo', 'dni', 'email', 'rol']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"El campo '{field}' es obligatorio."}), 400

    nuevo_usuario = Usuario(
        nombre_completo=data['nombre_completo'],
        dni=data['dni'],
        email=data['email'],
        rol=data['rol']
    )

    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario registrado exitosamente."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "El email o DNI ya están registrados."}), 409

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)

    POST /usuarios
Content-Type: application/json

{
  "nombre_completo": "Juan Pérez",
  "dni": "12345678",
  "email": "juan.perez@example.com",
  "rol": "Alumno"
}