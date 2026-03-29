"""Big Data Pipeline Monitor — Flask application."""
import os

from flask import Flask, jsonify, send_from_directory

from db import init_app
from routes.alerts import bp as alerts_bp
from routes.datasets import bp as datasets_bp
from routes.pipelines import bp as pipelines_bp
from routes.runs import bp as runs_bp

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')


def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='/static')
    app.config['JSON_SORT_KEYS'] = False

    init_app(app)

    # Register blueprints
    app.register_blueprint(datasets_bp)
    app.register_blueprint(pipelines_bp)
    app.register_blueprint(runs_bp)
    app.register_blueprint(alerts_bp)

    # Dashboard summary endpoint
    @app.get('/api/summary')
    def summary():
        from db import get_db
        db = get_db()
        datasets_count = db.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        pipelines_count = db.execute("SELECT COUNT(*) FROM pipelines").fetchone()[0]
        active_pipelines = db.execute("SELECT COUNT(*) FROM pipelines WHERE active=1").fetchone()[0]
        failed_runs_24h = db.execute(
            "SELECT COUNT(*) FROM job_runs WHERE status='failed' AND started_at >= datetime('now','-24 hours')"
        ).fetchone()[0]
        open_alerts = db.execute(
            "SELECT COUNT(*) FROM alert_events WHERE status='open'"
        ).fetchone()[0]
        recent_runs = db.execute(
            """SELECT r.id, r.status, r.started_at, r.finished_at, p.name AS pipeline_name
               FROM job_runs r
               LEFT JOIN pipelines p ON r.pipeline_id = p.id
               ORDER BY r.started_at DESC LIMIT 5"""
        ).fetchall()
        return jsonify({
            'datasets': datasets_count,
            'pipelines': pipelines_count,
            'active_pipelines': active_pipelines,
            'failed_runs_24h': failed_runs_24h,
            'open_alerts': open_alerts,
            'recent_runs': [dict(r) for r in recent_runs],
        })

    # Serve frontend pages
    @app.get('/')
    def index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.get('/<path:filename>')
    def frontend_file(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    # Generic error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
