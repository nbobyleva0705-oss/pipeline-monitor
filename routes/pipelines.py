"""Pipeline API routes."""
from flask import Blueprint, jsonify, request

from db import get_db
from services.pipeline_service import (
    create_pipeline,
    create_pipeline_version,
    get_all_pipelines,
    get_pipeline_by_id,
    get_pipeline_versions,
    patch_pipeline,
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


@bp.patch('/<pipeline_id>')
def update_pipeline(pipeline_id):
    data = request.get_json(silent=True) or {}
    pipeline = patch_pipeline(get_db(), pipeline_id, data)
    if not pipeline:
        return jsonify({'error': 'Pipeline not found'}), 404
    return jsonify(pipeline)


@bp.get('/<pipeline_id>/versions')
def list_versions(pipeline_id):
    pipeline = get_pipeline_by_id(get_db(), pipeline_id)
    if not pipeline:
        return jsonify({'error': 'Pipeline not found'}), 404
    return jsonify(get_pipeline_versions(get_db(), pipeline_id))


@bp.post('/<pipeline_id>/versions')
def add_version(pipeline_id):
    data = request.get_json(silent=True) or {}
    try:
        version = create_pipeline_version(get_db(), pipeline_id, data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(version), 201


@bp.post('/<pipeline_id>/run')
def run_pipeline(pipeline_id):
    try:
        run = create_run(get_db(), pipeline_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(run), 201
