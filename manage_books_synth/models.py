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
    title = StringField(max_length=100, required=True, unique=True)
    author = ListField(StringField(max_length=100, required=True))
    description = StringField(max_length=4096, required=False)
    genres = ListField(ReferenceField(Genre, reverse_delete_rule=NULLIFY))
    # books = ListField(ReferenceField(UniqueBook))
        
class Recherche(Document):
    day = DateTimeField(default=datetime.datetime.now)
    book = ReferenceField(Book)
    nb_searches = LongField()

    @queryset_manager
    def objects(doc_cls, queryset):
        # This may actually also be done by defining a default ordering for
        # the document, but this illustrates the use of manager methods
        return queryset.order_by('-date')

class UniqueBook(Document):
    """docstring for UniqueBook"""
    book = ReferenceField(Book)
    isbn = StringField(max_length=100, required=True, unique=False)
    image = URLField()
    last_update = DateTimeField(default=datetime.datetime.now)
