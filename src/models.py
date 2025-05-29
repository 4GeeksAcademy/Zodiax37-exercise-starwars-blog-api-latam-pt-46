from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

db = SQLAlchemy()

# Enum para tipo de favorito
class FavoriteType(enum.Enum):
    character = "character"
    planet = "planet"


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }


class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    gender: Mapped[str] = mapped_column(String(20))
    eye_color: Mapped[str] = mapped_column(String(20))
    height: Mapped[str] = mapped_column(String(10))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "eye_color": self.eye_color,
            "height": self.height
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(50))
    terrain: Mapped[str] = mapped_column(String(50))
    population: Mapped[str] = mapped_column(String(50))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }


class Favorite(db.Model):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    type: Mapped[FavoriteType] = mapped_column(Enum(FavoriteType), nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")

    # Relaciones uno a uno con las tablas específicas
    character_detail: Mapped["FavoriteCharacter"] = relationship("FavoriteCharacter", uselist=False, back_populates="favorite", cascade="all, delete-orphan")
    planet_detail: Mapped["FavoritePlanet"] = relationship("FavoritePlanet", uselist=False, back_populates="favorite", cascade="all, delete-orphan")

    def serialize(self):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value,
        }
        if self.type == FavoriteType.character and self.character_detail:
            data["character"] = self.character_detail.character.serialize()
        elif self.type == FavoriteType.planet and self.planet_detail:
            data["planet"] = self.planet_detail.planet.serialize()
        return data


class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_character"

    id: Mapped[int] = mapped_column(ForeignKey("favorite.id"), primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=False)

    favorite: Mapped["Favorite"] = relationship(back_populates="character_detail")
    character: Mapped["Character"] = relationship()

    def serialize(self):
        return {
            "favorite_id": self.id,
            "character": self.character.serialize()
        }


class FavoritePlanet(db.Model):
    __tablename__ = "favorite_planet"

    id: Mapped[int] = mapped_column(ForeignKey("favorite.id"), primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=False)

    favorite: Mapped["Favorite"] = relationship(back_populates="planet_detail")
    planet: Mapped["Planet"] = relationship()

    def serialize(self):
        return {
            "favorite_id": self.id,
            "planet": self.planet.serialize()
        }