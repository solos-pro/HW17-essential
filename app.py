# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    # genre = db.relationship('Movie', backref='genre', lazy=True)
    #
    # def __repr__(self):
    #     return '<Genre %r>' % self.name


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    # genre = fields.Str()


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    # genre = db.relationship('Genre')
    director_id = db.Column(db.Integer, db.ForeignKey('director.id'))
    # director = db.relationship('Director')

    def __repr__(self):
        return '<Movie %r>' % self.name


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Str()
    # Movie.genre = fields.Str()
    director_id = fields.Str()
# q1 = Movie.query.get(1)                               ###
# print(q1.director)


movie_schema = MovieSchema()
genre_schema = GenreSchema()
direct_schema = DirectorSchema()

api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        res = Movie.query
        if director_id is not None:
            res = res.filter(Movie.director_id == director_id)
        if genre_id is not None:
            res = res.filter(Movie.genre_id == genre_id)
        if genre_id is not None and director_id is not None:
            res = res.filter(Movie.genre_id == genre_id, Movie.director_id == director_id)
        result = res.all()

        return movie_schema.dump(result, many=True)

    def post(self):
        r_json = request.json
        add_movie = Movie(**r_json)
        with db.session.begin():
            db.session.add(add_movie)
        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404
        return movie_schema.dump(movie)

    def put(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404

        movie.title = request.json.get("title")
        movie.description = request.json.get("description")
        movie.trailer = request.json.get("trailer")
        movie.year = request.json.get("year")
        movie.rating = request.json.get("rating")
        movie.genre_id = request.json.get("genre_id")
        movie.director_id = request.json.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


# ------------------------------------------------------------------


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genre_id = request.args.get('genre_id')
        res = Genre.query
        if genre_id is not None:
            res = res.filter(Genre.id == genre_id)
        result = res.all()
        return genre_schema.dump(result, many=True)

    def post(self):
        r_json = request.json
        add_genre = Genre(**r_json)
        with db.session.begin():
            db.session.add(add_genre)
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        genre = Genre.query.get(uid)
        if not genre:
            return "", 404
        return genre_schema.dump(genre)

    def put(self, uid):
        genre = Genre.query.get(uid)
        if not genre:
            return "", 404

        genre.title = request.json.get("genre_id")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, uid):
        genre = Genre.query.get(uid)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
