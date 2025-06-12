from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, default=True)

    favorite_people = relationship("UserFavoritePeople", back_populates="user")
    favorite_planets = relationship(
        "UserFavoritePlanet", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
        }


class Planet(db.Model):
    __tablename__ = 'planets'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    diameter: Mapped[str] = mapped_column(String(20), nullable=False)
    rotation_period: Mapped[str] = mapped_column(String(20), nullable=False)
    orbital_period: Mapped[str] = mapped_column(String(20), nullable=False)
    gravity: Mapped[str] = mapped_column(String(10), nullable=False)
    population: Mapped[str] = mapped_column(String(30), nullable=False)
    climate: Mapped[str] = mapped_column(String(50), nullable=False)
    terrain: Mapped[str] = mapped_column(String(50), nullable=False)
    surface_water: Mapped[str] = mapped_column(String(50), nullable=False)

    residents = relationship("People", back_populates="homeworld")
    user_favorites = relationship(
        "UserFavoritePlanet", back_populates="planet")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'diameter': self.diameter,
            'rotation_period': self.rotation_period,
            'orbital_period': self.orbital_period,
            'gravity': self.gravity,
            'population': self.population,
            'climate': self.climate,
            'terrain': self.terrain,
            'surface_water': self.surface_water
        }


class People(db.Model):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    height: Mapped[str] = mapped_column(String(10), nullable=False)
    mass: Mapped[str] = mapped_column(String(10), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(10), nullable=False)
    skin_color: Mapped[str] = mapped_column(String(10), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(10), nullable=False)
    birth_year: Mapped[str] = mapped_column(String(10), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    homeworld_id: Mapped[int] = mapped_column(
        ForeignKey('planets.id'), nullable=True)

    homeworld = relationship("Planet", back_populates="residents")
    user_favorites = relationship(
        "UserFavoritePeople", back_populates="people")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'mass': self.mass,
            'hair_color': self.hair_color,
            'skin_color': self.skin_color,
            'eye_color': self.eye_color,
            'birth_year': self.birth_year,
            'gender': self.gender,
            'homeworld': self.homeworld_id
        }


class UserFavoritePlanet(db.Model):
    __tablename__ = 'user_favorite_planets'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), primary_key=True)
    planet_id: Mapped[int] = mapped_column(
        ForeignKey('planets.id'), primary_key=True)

    user = relationship("User", back_populates="favorite_planets")
    planet = relationship("Planet", back_populates="user_favorites")

    def serialize(self):
        return {
            'user_id': self.user_id,
            'planet_id': self.planet_id,

        }


class UserFavoritePeople(db.Model):
    __tablename__ = 'user_favorite_people'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), primary_key=True)
    people_id: Mapped[int] = mapped_column(
        ForeignKey('people.id'), primary_key=True)

    user = relationship("User", back_populates="favorite_people")
    people = relationship("People", back_populates="user_favorites")

    def serialize(self):
        return {
            'user_id': self.user_id,
            'people_id': self.people_id,

        }
