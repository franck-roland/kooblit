from mongoengine import *
import datetime

class SubGenre(Document):
    """docstring for SubGenre"""
    genre = StringField(max_length=100, required=True)

class Genre(Document):
    """docstring for Genre"""
    genre = StringField(max_length=100, required=True)
    sub_genre = ListField(ReferenceField(SubGenre))

class UniqueBook(Document):
    """docstring for UniqueBook"""
    isbn = StringField(max_length=100, required=True, unique=True)
    image = URLField()
    last_update = DateTimeField(default=datetime.datetime.now)

# Create your models here.
class Book(Document):
    title = StringField(max_length=100, required=True)
    author = ListField(StringField(max_length=100, required=True))
    description = StringField(max_length=4096, required=False)
    books = ListField(ReferenceField(UniqueBook))
    genres = ListField(ReferenceField(Genre, reverse_delete_rule=NULLIFY))
    nb_search = LongField()



