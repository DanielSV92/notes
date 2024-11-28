
import datetime
import json

class L(list):
    """
    A subclass of list that can accept additional attributes.
    Should be able to be used just like a regular list.

    The problem:
    a = [1, 2, 4, 8]
    a.x = "Hey!" # AttributeError: 'list' object has no attribute 'x'

    The solution:
    a = L(1, 2, 4, 8)
    a.x = "Hey!"
    """

    def __new__(self, *args, **kwargs):
        return super(L, self).__new__(self, args, kwargs)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            list.__init__(self, args[0])
        else:
            list.__init__(self, args)
        self.__dict__.update(kwargs)

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        return self


user = L('user')
user.update = L()
user.id = 1
user.email = 'test@test.com'
user.first_name = 'mr'
user.last_name = 'temp'
user.password = 'notsecurepassword'

user2 = L('user')
user2.update = L()
user2.id = 2
user2.email = 'test2@test.com'
user2.first_name = 'mr'
user2.last_name = 'temp'
user2.password = 'notsecurepassword'

user_dict = {
    'id': user.id,
    'email': user.email,
    'first_name': user.first_name,
    'last_name': user.last_name
}

note = L('note')
note.delete = L()
note.note_id = 1
note.owner_id = 1
note.note_description = 'some cool note'

note2 = L('note')
note2.note_id = 2
note2.owner_id = 2
note2.note_description = 'another awesome txt'

note_list =  [
    {
        'note_id': note.note_id,
        'owner_id': note.owner_id,
        'note_description': note.note_description
    }
]

shared_list = [
    {
        'note_id': note2.note_id,
        'user_id': user.id
    }
]

shared_note = L('note_share')
shared_note.note_id = note2.note_id
shared_note.user_id = user2.id
