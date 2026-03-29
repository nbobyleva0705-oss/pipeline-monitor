"""Pipeline API routes."""
from flask import Blueprint, jsonify, request

from db import get_db
from services.pipeline_service import (
    create_pipeline,
    get_all_pipelines,
    get_pipeline_by_id,
    validate_pipeline,
)
from services.run_service import create_run

bp = Blueprint('pipelines', __name__, url_prefix='/pipelines')


@bp.get('/')
def list_pipelines():
    return jsonify(get_all_pipelines(get_db()))


@bp.post('/')
def create():
    data = request.get_json(silent=True) or {}
    errors = validate_pipeline(data)
    if errors:
        return jsonify({'error': ', '.join(errors)}), 400
    try:
        pipeline = create_pipeline(get_db(), data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(pipeline), 201


@bp.get('/<pipeline_id>')
def get_one(pipeline_id):
    pipeline = get_pipeline_by_id(get_db(), pipeline_id)
    if not pipeline:
        return jsonify({'error': 'Pipeline not found'}), 404
    return jsonify(pipeline)


@bp.post('/<pipeline_id>/run')
def run_pipeline(pipeline_id):
    try:
        run = create_run(get_db(), pipeline_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(run), 201
