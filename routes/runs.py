"""JobRun API routes."""
from flask import Blueprint, jsonify, request

from db import get_db
from services.run_service import get_run_by_id, get_runs, patch_run

bp = Blueprint('runs', __name__, url_prefix='/runs')


@bp.get('/')
def list_runs():
    pipeline_id = request.args.get('pipeline_id')
    status = request.args.get('status')
    date = request.args.get('date')
    return jsonify(get_runs(get_db(), pipeline_id=pipeline_id, status=status, date=date))


@bp.get('/<run_id>')
def get_one(run_id):
    run = get_run_by_id(get_db(), run_id)
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    return jsonify(run)


@bp.patch('/<run_id>')
def update_run(run_id):
    data = request.get_json(silent=True) or {}
    try:
        run = patch_run(get_db(), run_id, data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    if not run:
        return jsonify({'error': 'Run not found'}), 404
    return jsonify(run)
