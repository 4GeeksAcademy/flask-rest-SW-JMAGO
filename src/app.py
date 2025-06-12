"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, UserFavoritePlanet, UserFavoritePeople
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people])


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'error': 'Person not found'}), 404
    return jsonify(person.serialize())

# Planets endpoints


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets])


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'error': 'Planet not found'}), 404
    return jsonify(planet.serialize())

# Users endpoints


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])


@app.route('/users/<int:users_id>', methods=['GET'])
def get_users(users_id):
    user = User.query.get(users_id)
    if user is None:
        return jsonify({'error': 'Person not found'}), 404
    return jsonify(user.serialize())


def get_current_user():
    # In a real app, this would be based on authentication
    # For demo purposes, we'll just return the first user
    return User.query.first()


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    favorite_people = [fav.people.serialize()
                       for fav in current_user.favorite_people]
    favorite_planets = [fav.planet.serialize()
                        for fav in current_user.favorite_planets]

    return jsonify({
        'favorite_people': favorite_people,
        'favorite_planets': favorite_planets
    })


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    try:

        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'user_id is required in request body'}), 400

        user_id = data['user_id']
        current_user = User.query.get(user_id)

        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        # Verificar si el planeta existe
        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({'error': 'Planet not found'}), 404

        # Verificar si ya es favorito
        existing_fav = UserFavoritePlanet.query.filter_by(
            user_id=current_user.id,
            planet_id=planet_id
        ).first()

        if existing_fav:
            return jsonify({'message': 'Planet already in favorites'}), 200

        # Crear nueva relación favorita
        new_fav = UserFavoritePlanet(
            user_id=current_user.id,
            planet_id=planet_id
        )

        db.session.add(new_fav)
        db.session.commit()

        return jsonify({
            'message': 'Planet added to favorites',
            'planet': planet.serialize(),
            'user': current_user.serialize()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'user_id is required in request body'}), 400

        user_id = data['user_id']
        current_user = User.query.get(user_id)

        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        # Verificar si la persona existe
        people = People.query.get(people_id)
        if not people:
            return jsonify({'error': 'People not found'}), 404

        # Verificar si ya es favorito
        existing_fav = UserFavoritePeople.query.filter_by(
            user_id=current_user.id,
            people_id=people_id
        ).first()

        if existing_fav:
            return jsonify({'message': 'People already in favorites'}), 200

        # Crear nueva relación favorita
        new_fav = UserFavoritePeople(
            user_id=current_user.id,
            people_id=people_id
        )

        db.session.add(new_fav)
        db.session.commit()

        return jsonify({
            'message': 'People added to favorites',
            'people': people.serialize(),
            'user': current_user.serialize()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        favorite = UserFavoritePlanet.query.filter_by(
            user_id=current_user.id,
            planet_id=planet_id
        ).first()

        if not favorite:
            return jsonify({'error': 'Favorite planet not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'message': 'Planet removed from favorites successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        favorite = UserFavoritePeople.query.filter_by(
            user_id=current_user.id,
            people_id=people_id
        ).first()

        if not favorite:
            return jsonify({'error': 'Favorite person not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'message': 'Person removed from favorites successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
