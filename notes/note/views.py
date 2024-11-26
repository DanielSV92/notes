from flask import Blueprint
from flask import Response
from flask import jsonify
from flask import request

from notes.note import controller
from notes.auth.views import token_required

blueprint = Blueprint('note', __name__, url_prefix='/note')


@blueprint.route('/create_note',
                 methods=['POST'])
@token_required
def create_note(current_user):
    body = request.get_json()
    note = controller.create_note(current_user, body)
    return jsonify(note)


@blueprint.route('/update_note/<note_id>',
                 methods=['PATCH'])
@token_required
def update_note(current_user, note_id):
    body = request.get_json()
    note = controller.update_note(current_user, note_id, body)
    return jsonify(note)


@blueprint.route('/delete_note/<note_id>',
                 methods=['DELETE'])
@token_required
def delete_note(current_user, note_id):
    controller.delete_note(current_user, note_id)

    response = Response(None, status=204)
    response.headers.remove('Content-Type')

    return response


@blueprint.route('/get_note/<note_id>',
                 methods=['GET'])
@token_required
def get_note(current_user, note_id):
    note = controller.get_note(current_user, note_id)
    return jsonify(note)


@blueprint.route('/get_notes', methods=['GET'])
@token_required
def get_all_notes(current_user):
    note_list = controller.get_all_notes(current_user)
    return jsonify(note_list)


@blueprint.route('/share_note/<note_id>/share/<share_id>',
                 methods=['POST'])
@token_required
def create_note(current_user, note_id, share_id):
    note = controller.share_note(current_user, note_id, share_id)
    return jsonify(note)


@blueprint.route('/search_notes', methods=['GET'])
@token_required
def get_all_notes(current_user):
    body = request.args.to_dict()
    note_list = controller.search_note(current_user, body)
    return jsonify(note_list)