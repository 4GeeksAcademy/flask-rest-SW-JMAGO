import os
from flask_admin import Admin
from models import db, User, Planet, People, UserFavoritePlanet, UserFavoritePeople
from flask_admin.contrib.sqla import ModelView


class UserFavoritePlanetView(ModelView):
    column_list = ('user_id', 'planet_id', 'user', 'planet')
    form_columns = ('user_id', 'planet_id')


class UserFavoritePeopleView(ModelView):
    column_list = ('user_id', 'people_id', 'user', 'people')
    form_columns = ('user_id', 'people_id')


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(UserFavoritePlanetView(
        UserFavoritePlanet, db.session, name="Favorite Planets"))
    admin.add_view(UserFavoritePeopleView(
        UserFavoritePeople, db.session, name="Favorite People"))
