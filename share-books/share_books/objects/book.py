from share_books import utils
from share_books.app import mongo
from share_books.objects.base import Base
from share_books import errors

class Book(Base):
    def __init__(self, _id, user_id, author, title, description, **kwargs):
        self._id = _id
        self.user_id = user_id
        self.author = author
        self.title = title
        self.description = description
        self.picture = kwargs.get('picture')
        self.deposit = float(kwargs.get('deposit') or 0.0)
        self.rent_per_day = float(kwargs.get('rent_per_day') or self.deposit / 100.0)

    def to_dict(self):
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'author': self.author,
            'title': self.title,
            'description': self.description,
            'picture': self.picture,
            'deposit': self.deposit,
            'rent_per_day': self.rent_per_day,
        }

    def update(self, **kwargs):
        self.author = kwargs.get('author', self.author)
        self.title = kwargs.get('title', self.title)
        self.description = kwargs.get('description', self.description)
        self.picture = kwargs.get('picture', self.picture)
        self.deposit = kwargs.get('deposit', self.deposit)
        self.rent_per_day = kwargs.get('rent_per_day', self.rent_per_day)
        return self.to_dict()

    @classmethod
    def get_by_id(cls, _id):
        book = mongo.db.books.find_one({'_id': _id})
        if not book:
            return None
        return cls(**book)

    @classmethod
    def get_by_user_id(cls, user_id):
        cursor = mongo.db.books.find({'user_id': user_id})
        for book in cursor:
            yield cls(**book)

    @classmethod
    def get_by_author(cls, author):
        cursor = mongo.db.books.find({'author': author})
        for book in cursor:
            yield cls(**book)

    @classmethod
    def get_all(cls):
        cursor = mongo.db.books.find()
        for book in cursor:
            yield cls(**book)

    @classmethod
    def delete_by_id(cls, _id):
        if not mongo.db.books.find_one({'_id': _id}):
            raise errors.NotFound()
        mongo.db.books.remove({'_id': _id})

    @classmethod
    def new(cls, **kwargs):
        kwargs.setdefault('_id', utils.gen_id())
        return cls(**kwargs)

    def save(self):
        mongo.db.books.save(self.to_dict())
