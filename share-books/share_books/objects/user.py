from share_books.app import passlib

from share_books.app import mongo
from share_books import utils
from share_books.objects.base import Base
from share_books import errors

class User(Base):
    def __init__(self, _id, email, encrypted_password, **kwargs):
        self._id = _id
        self._email = email
        self._encrypted_password = encrypted_password

    def to_dict(self):
        return {
            '_id': self._id,
            'email': self._email,
            'encrypted_password': self._encrypted_password,
        }

    def update(self, **kwargs):
        self._email = kwargs.get('email', self._email)
        self._encrypted_password = kwargs.get(
            'encrypted_password', self._encrypted_password)
        return self.to_dict()

    @classmethod
    def get_by_id(cls, _id):
        _dict = mongo.db.users.find_one({'_id': _id})
        if not _dict:
            return None
        return cls(**_dict)

    @classmethod
    def get_by_email(cls, email):
        _dict = mongo.db.users.find_one({'email': email})
        if not _dict:
            return None
        return cls(**_dict)

    @classmethod
    def encrypt_password(cls, password):
        return passlib.encrypt(password, salt_length=16)

    def authenticate(self, password):
        return passlib.verify(password, self._encrypted_password)

    # @classmethod
    # def encrypt_password(cls, password):
    #     return password

    # def authenticate(self, password):
    #     return self._encrypted_password == password

    @classmethod
    def delete_by_id(cls, _id):
        if not mongo.db.users.find_one({'_id': _id}):
            raise errors.NotFound()
        # mongo.db.users.delete_one({'_id': _id})
        mongo.db.users.remove({'_id': _id})

    @classmethod
    def new(cls, **kwargs):
        kwargs.setdefault('_id', utils.gen_id())
        kwargs.setdefault('encrypted_password',
                          cls.encrypt_password(kwargs['password']))
        return cls(**kwargs)

    def save(self):
        _dict = self.to_dict()
        # mongo.db.users.replace_one({'_id': self._id}, _dict, upsert=True)
        mongo.db.users.save(_dict)
