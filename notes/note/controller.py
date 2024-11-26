import section.errors as error

from section.note.utils import note_to_dict
from section.domain.models import Notes
from section.domain.models import NoteShare
from section.domain.models import user_datastore
from section.extensions import db

def create_note(current_user, body):
    note_description = body.get('note_description')

    note = Notes(
        owner_id=current_user.user_id,
        note_description=note_description)
    note.add()
    db.session.commit()

    note_dict = note_to_dict(note)

    return note_dict


def get_note(current_user, note_id):
    note = Notes.query.filter(
        Notes.owner_id == current_user.user_id,
        Notes.note_id == note_id).first()

    if note:
        note = note_to_dict(note)

    return note


def get_all_notes(current_user):
    notes_list = Notes.query.filter(
        Notes.owner_id == current_user.user_id).all()

    return [note_to_dict(note) for note in notes_list]


def update_note(current_user, note_id, body):
    note = Notes.query.filter(
        Notes.note_id == note_id,
        Notes.owner_id == current_user.user_id).first()

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
        Notes.owner_id == current_user.user_id,
        Notes.note_id == note_id).first()

    if not note:
        raise error.NotFound(message='The note does not exist')

    note.delete()
    db.session.commit()



def share_note(current_user, note_id, share_id):
    user = user_datastore.get_user(share_id)

    if not user:
        raise error.BadRequest('Invalid user to share note')

    note = Notes.query.filter(
        Notes.note_id == note_id,
        Notes.owner_id == current_user.user_id).first()

    if not note:
        raise error.NotFound(message='The note does not exist')
    
    share_note = NoteShare(
        note_id=note_id,
        user_id=share_id
    )

    note.add()
    db.session.commit()

    note = note_to_dict(note)
    note['share_id'] = share_note.user_id

    return note


def search_note(current_user, body):
    query = body.get('query')
    notes_list = Notes.query.filter(
        Notes.owner_id == current_user.user_id,
        Notes.note_description.contains(query)).all()

    return [note_to_dict(note) for note in notes_list]
