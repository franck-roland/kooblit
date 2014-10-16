from django.conf import settings
import datetime
import mongoengine


class Theme(mongoengine.Document):
    """docstring for Theme"""
    theme = mongoengine.StringField(max_length=100, required=True, unique=True)
    sub_theme = mongoengine.ListField(mongoengine.ReferenceField('Theme'))
    amazon_id = mongoengine.LongField(default=None, unique=True)


class Book(mongoengine.Document):
    small_title = mongoengine.StringField(max_length=32, required=True, unique=False)
    title = mongoengine.StringField(max_length=settings.MAX_BOOK_TITLE_LEN, required=True, unique=True)
    author = mongoengine.ListField(mongoengine.StringField(max_length=100, required=True))
    description = mongoengine.StringField(max_length=4096, required=False)
    themes = mongoengine.ListField(mongoengine.ReferenceField(Theme, reverse_delete_rule=mongoengine.NULLIFY))
    langue = mongoengine.StringField(max_length=32, unique=False)
    # books = mongoengine.ListField(mongoengine.ReferenceField(UniqueBook))


class Recherche(mongoengine.Document):
    day = mongoengine.DateTimeField(default=datetime.datetime.now)
    book = mongoengine.ReferenceField(Book)
    nb_searches = mongoengine.LongField()

    @mongoengine.queryset_manager
    def objects(doc_cls, queryset):
        # This may actually also be done by defining a default ordering for
        # the mongoengine.document, but this illustrates the use of manager methods
        return queryset.order_by('-date')


class UniqueBook(mongoengine.Document):
    """docstring for UniqueBook"""
    book = mongoengine.ReferenceField(Book)
    isbn = mongoengine.StringField(max_length=100, required=True, unique=False)
    image = mongoengine.URLField()
    medium_image = mongoengine.URLField()
    last_update = mongoengine.DateTimeField(default=datetime.datetime.now)
    buy_url = mongoengine.URLField()
    editeur = mongoengine.StringField(max_length=100)
