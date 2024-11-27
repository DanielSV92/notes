import notes.errors as error

from notes.note.utils import note_to_dict
from notes.domain.models import Notes
from notes.domain.models import NoteShare
from notes.domain.models import User
from notes.extensions import db

def create_note(current_user, body):
    note_description = body.get('note_description')

    note = Notes(
        owner_id=current_user.id,
        note_description=note_description)
    note.add()
    db.session.commit()

    note_dict = note_to_dict(note)

    return note_dict


def get_note(current_user, note_id):
    note = Notes.query.filter(
        Notes.owner_id == current_user.id,
        Notes.note_id == note_id).first()

    if not note:
        raise error.NotFound('Note does not exist')

    return note_to_dict(note)


def get_all_notes(current_user):
    notes_list = Notes.query.filter(
        Notes.owner_id == current_user.id).all()
    
    reference_list = NoteShare.query.filter(
        NoteShare.user_id == current_user.id
    ).all()
    shared_list = []
    for item in reference_list:
        shared_note = Notes.query.filter(
            Notes.note_id == item['note_id']
        ).first()
        shared_list.append(shared_note)

    body = {
        'my_notes': [note_to_dict(note) for note in notes_list],
        'shared_with_me': [note_to_dict(note) for note in shared_list]
    }

    return body


def update_note(current_user, note_id, body):
    note = Notes.query.filter(
        Notes.note_id == note_id,
        Notes.owner_id == current_user.id).first()

    if not note:
        raise error.NotFound(message='The note does not exist')

    note_description = body.get('note_description')
    if note_description:
        note.note_description = note_description

    db.session.commit()

    note = note_to_dict(note)

    return note


def delete_note(current_user, note_id):
    note = Notes.query.filter(
        Notes.owner_id == current_user.id,
        Notes.note_id == note_id).first()

    if not note:
        raise error.NotFound(message='The note does not exist')

    note.delete()
    db.session.commit()



def share_note(current_user, note_id, share_id):
    if share_id == current_user.id:
        raise error.BadRequest('You can not share a note to yourself')

    user = User.query.filter(User.id == share_id).first()

    if not user:
        raise error.BadRequest('Invalid user to share note')

    note = Notes.query.filter(
        Notes.note_id == note_id,
        Notes.owner_id == current_user.id).first()

    if not note:
        raise error.NotFound(message='The note does not exist')
    
    share_note = NoteShare(
        note_id=note_id,
        user_id=share_id
    )

    share_note.add()
    db.session.commit()

    note = note_to_dict(note)
    note['share_id'] = share_note.user_id

    return note


def search_note(current_user, body):
    query = body.get('query')
    notes_list = Notes.query.filter(
        Notes.owner_id == current_user.id,
        Notes.note_description.contains(query)).all()

    reference_list = NoteShare.query.filter(
        NoteShare.user_id == current_user.id).all()
    
    shared_list = []
    for item in reference_list:
        shared_note = Notes.query.filter(
            Notes.note_id == item.note_id,
            Notes.note_description.contains(query)).first()
        shared_list.append(shared_note)

    body = {
        'my_notes': [note_to_dict(note) for note in notes_list],
        'shared_with_me': [note_to_dict(note) for note in shared_list]
    }

    return body
