from mongoengine import *
import datetime

class SubGenre(Document):
    """docstring for SubGenre"""
    genre = StringField(max_length=100, required=True)

class Genre(Document):
    """docstring for Genre"""
    genre = StringField(max_length=100, required=True)
    sub_genre = ListField(ReferenceField(SubGenre))

class Book(Document):
    small_title = StringField(max_length=32, required=True, unique=True)
    title = StringField(max_length=100, required=True)
    auteur = ListField(StringField(max_length=100, required=True))
    description = StringField(max_length=4096, required=False)
    genres = ListField(ReferenceField(Genre, reverse_delete_rule=NULLIFY))
    nb_searches = ListField(LongField())
    # books = ListField(ReferenceField(UniqueBook))
        

class UniqueBook(Document):
    """docstring for UniqueBook"""
    book = ReferenceField(Book)
    isbn = StringField(max_length=100, required=True, unique=True)
    image = URLField()
    last_update = DateTimeField(default=datetime.datetime.now)
