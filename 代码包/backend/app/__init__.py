"""Flask 应用工厂"""
import os
from flask import Flask, send_file
from flask_cors import CORS
from .config import config_map
from .extensions import init_extensions


def create_app(env='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[env])
    CORS(app, supports_credentials=True)
    init_extensions(app)
    from .common.errors import register_error_handlers
    register_error_handlers(app)
    register_blueprints(app)

    # 提供前端静态页面（开发阶段避免 CORS 问题）
    _ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @app.route('/admin')
    @app.route('/admin/login')
    def serve_admin_login():
        return send_file(os.path.join(_ROOT, 'frontend', 'admin-web', 'login.html'))

    return app


def register_blueprints(app):
    # common (3)
    from .controllers.common.sms_controller import bp as sms_bp
    from .controllers.common.upload_controller import bp as upload_bp
    from .controllers.common.captcha_controller import bp as captcha_bp

    # user (3) — delivery_controller / mall_controller 待合作
    from .controllers.user.auth_controller import bp as user_auth_bp
    from .controllers.user.info_controller import bp as user_info_bp
    from .controllers.user.point_controller import bp as user_point_bp

    # device (2) — delivery/session/batch/heartbeat 待合作
    from .controllers.device.auth_controller import bp as device_auth_bp
    from .controllers.device.status_controller import bp as device_status_bp

    # admin (3) — device/rule/model/statistics/merchant/report/role/log 待合作
    from .controllers.admin.auth_controller import bp as admin_auth_bp
    from .controllers.admin.area_controller import bp as admin_area_bp
    from .controllers.admin.user_controller import bp as admin_user_bp

    # merchant (2) — commodity/order/report/statistics/sub_account/apply 待合作
    from .controllers.merchant.auth_controller import bp as merchant_auth_bp
    from .controllers.merchant.info_controller import bp as merchant_info_bp

    # 注册 blueprint
    app.register_blueprint(sms_bp, url_prefix='/api/v1/common')
    app.register_blueprint(upload_bp, url_prefix='/api/v1/common')
    app.register_blueprint(captcha_bp, url_prefix='/api/v1/common')

    app.register_blueprint(user_auth_bp, url_prefix='/api/v1/user')
    app.register_blueprint(user_info_bp, url_prefix='/api/v1/user')
    app.register_blueprint(user_point_bp, url_prefix='/api/v1/user')

    app.register_blueprint(device_auth_bp, url_prefix='/api/v1/device')
    app.register_blueprint(device_status_bp, url_prefix='/api/v1/device')

    app.register_blueprint(admin_auth_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_area_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_user_bp, url_prefix='/api/v1/admin')

    app.register_blueprint(merchant_auth_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_info_bp, url_prefix='/api/v1/merchant')