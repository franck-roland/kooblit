from django.conf import settings
from mongoengine import *
import datetime


class Theme(Document):
    """docstring for Theme"""
    theme = StringField(max_length=100, required=True, unique=True)
    sub_theme = ListField(ReferenceField('Theme'))
    amazon_id = LongField(default=None, unique=True)


class Book(Document):
    small_title = StringField(max_length=32, required=True, unique=False)
    title = StringField(max_length=settings.MAX_BOOK_TITLE_LEN, required=True, unique=True)
    author = ListField(StringField(max_length=100, required=True))
    description = StringField(max_length=4096, required=False)
    themes = ListField(ReferenceField(Theme, reverse_delete_rule=NULLIFY))
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
    buy_url = URLField()
