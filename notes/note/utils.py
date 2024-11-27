def note_to_dict(note) -> dict:
    if note:
        return {
            'note_id': note.note_id,
            'note_description': note.note_description
        }
