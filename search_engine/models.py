import datetime
import mongoengine


class SubGenre(mongoengine.Document):
    """docstring for SubGenre"""
    genre = mongoengine.StringField(max_length=100, required=True)

class Genre(mongoengine.Document):
    """docstring for Genre"""
    genre = mongoengine.StringField(max_length=100, required=True)
    sub_genre = mongoengine.ListField(mongoengine.ReferenceField(SubGenre))

class UniqueBook(mongoengine.Document):
    """docstring for UniqueBook"""
    isbn = mongoengine.StringField(max_length=100, required=True, unique=True)
    image = mongoengine.URLField()
    last_update = mongoengine.DateTimeField(default=datetime.datetime.now)

# Create your models here.
class Book(mongoengine.Document):
    title = mongoengine.StringField(max_length=100, required=True)
    author = mongoengine.ListField(mongoengine.StringField(max_length=100, required=True))
    description = mongoengine.StringField(max_length=4096, required=False)
    books = mongoengine.ListField(mongoengine.ReferenceField(UniqueBook))
    genres = mongoengine.ListField(mongoengine.ReferenceField(Genre, reverse_delete_rule=mongoengine.NULLIFY))
    nb_search = mongoengine.LongField()



