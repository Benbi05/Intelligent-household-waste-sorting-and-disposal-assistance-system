"""
AI Service Flask Application Entry Point
Registers blueprints for recognition, analysis, and model management APIs.
"""
from flask import Flask
from 代码包.ai_service.config import logger

def create_app():
    """Create and configure the AI service Flask application."""
    app = Flask(__name__)

    # Register API blueprints
    from 代码包.ai_service.api.recognize_api import recognize_bp
    from 代码包.ai_service.api.analysis_api import analysis_bp
    from 代码包.ai_service.api.model_api import model_bp

    app.register_blueprint(recognize_bp, url_prefix='/ai')
    app.register_blueprint(analysis_bp, url_prefix='/ai')
    app.register_blueprint(model_bp, url_prefix='/ai')

    # Health check endpoint
    @app.route('/ai/health', methods=['GET'])
    def health_check():
        return {'code': 200, 'message': 'AI Service OK', 'data': None}

    logger.info('AI Service initialized with all blueprints registered')
    return app


# Create app instance for gunicorn / flask run
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
