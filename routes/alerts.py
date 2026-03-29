"""AlertRule and AlertEvent API routes."""
from flask import Blueprint, jsonify, request

from db import get_db
from services.alert_service import (
    create_alert_rule,
    delete_alert_rule,
    get_alert_by_id,
    get_alert_rule_by_id,
    get_all_alert_rules,
    get_all_alerts,
    patch_alert_rule,
    validate_alert_rule,
)

bp = Blueprint('alerts', __name__)


# --- Alert Rules ---

@bp.get('/alert-rules/')
def list_rules():
    return jsonify(get_all_alert_rules(get_db()))


@bp.post('/alert-rules/')
def create_rule():
    data = request.get_json(silent=True) or {}
    errors = validate_alert_rule(data)
    if errors:
        return jsonify({'error': ', '.join(errors)}), 400
    try:
        rule = create_alert_rule(get_db(), data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(rule), 201


@bp.get('/alert-rules/<rule_id>')
def get_rule(rule_id):
    rule = get_alert_rule_by_id(get_db(), rule_id)
    if not rule:
        return jsonify({'error': 'Alert rule not found'}), 404
    return jsonify(rule)


@bp.patch('/alert-rules/<rule_id>')
def update_rule(rule_id):
    data = request.get_json(silent=True) or {}
    rule = patch_alert_rule(get_db(), rule_id, data)
    if not rule:
        return jsonify({'error': 'Alert rule not found'}), 404
    return jsonify(rule)


@bp.delete('/alert-rules/<rule_id>')
def remove_rule(rule_id):
    deleted = delete_alert_rule(get_db(), rule_id)
    if not deleted:
        return jsonify({'error': 'Alert rule not found'}), 404
    return '', 204


# --- Alert Events ---

@bp.get('/alerts/')
def list_alerts():
    return jsonify(get_all_alerts(get_db()))


@bp.get('/alerts/<alert_id>')
def get_alert(alert_id):
    alert = get_alert_by_id(get_db(), alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    return jsonify(alert)
