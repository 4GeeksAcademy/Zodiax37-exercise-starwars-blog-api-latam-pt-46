"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite, FavoriteCharacter, FavoritePlanet, FavoriteType

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de base de datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Manejo de errores
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Sitemap
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Endpoint de prueba
@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Prueba"
    }
    return jsonify(response_body), 200

# ---------------------- RUTAS Get ----------------------

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([usr.serialize() for usr in users]), 200



# Obtener todos los personajes
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([char.serialize() for char in characters]), 200

# Obtener todos los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

# Obtener favoritos de un usuario
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([fav.serialize() for fav in favorites]), 200

# Agregar un favorito (character o planet)
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get("user_id")
    favorite_type = data.get("type")
    entity_id = data.get("entity_id")  # ID del personaje o planeta

    if not user_id or not favorite_type or not entity_id:
        return jsonify({"error": "Missing user_id, type, or entity_id"}), 400

    if favorite_type == "character":
        favorite = Favorite(user_id=user_id, type=FavoriteType.character)
        db.session.add(favorite)
        db.session.flush()  # Para obtener ID antes de commit
        fav_char = FavoriteCharacter(id=favorite.id, character_id=entity_id)
        db.session.add(fav_char)

    elif favorite_type == "planet":
        favorite = Favorite(user_id=user_id, type=FavoriteType.planet)
        db.session.add(favorite)
        db.session.flush()
        fav_planet = FavoritePlanet(id=favorite.id, planet_id=entity_id)
        db.session.add(fav_planet)

    else:
        return jsonify({"error": "Invalid favorite type"}), 400

    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Eliminar un favorito
@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200


# ---------------------- POST PARA CREAR DATOS (Users, Characters, Planets) ----------------------

# Crear un usuario
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(email=email, password=password, is_active=True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# Crear un personaje
@app.route('/characters', methods=['POST'])
def create_character():
    data = request.json
    name = data.get('name')
    gender = data.get('gender')
    eye_color = data.get('eye_color')
    height = data.get('height')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    new_character = Character(name=name, gender=gender, eye_color=eye_color, height=height)
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201

# Crear un planeta
@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.json
    name = data.get('name')
    climate = data.get('climate')
    terrain = data.get('terrain')
    population = data.get('population')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    new_planet = Planet(name=name, climate=climate, terrain=terrain, population=population)
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

# --------------------------------------------

# Ejecutar servidor
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
