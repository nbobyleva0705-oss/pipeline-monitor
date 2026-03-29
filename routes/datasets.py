"""Dataset API routes."""
from flask import Blueprint, jsonify, request

from db import get_db
from services.dataset_service import (
    create_dataset,
    get_all_datasets,
    get_dataset_by_id,
    validate_dataset,
)

bp = Blueprint('datasets', __name__, url_prefix='/datasets')


@bp.get('/')
def list_datasets():
    return jsonify(get_all_datasets(get_db()))


@bp.post('/')
def create():
    data = request.get_json(silent=True) or {}
    errors = validate_dataset(data)
    if errors:
        return jsonify({'error': ', '.join(errors)}), 400
    try:
        dataset = create_dataset(get_db(), data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(dataset), 201


@bp.get('/<dataset_id>')
def get_one(dataset_id):
    dataset = get_dataset_by_id(get_db(), dataset_id)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    return jsonify(dataset)
