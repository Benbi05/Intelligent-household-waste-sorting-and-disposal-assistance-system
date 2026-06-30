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

    # 提供前端静态页面
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 管理后台（Vue 构建产物）
    @app.route('/admin')
    @app.route('/admin/<path:subpath>')
    def serve_admin(subpath=''):
        return send_file(os.path.join(_BASE, 'admin_dist', 'index.html'))

    # 静态资源（JS/CSS/图片）
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_file(os.path.join(_BASE, 'admin_dist', 'assets', filename))

    # 商家后台（Vue 构建产物）
    @app.route('/merchant')
    @app.route('/merchant/<path:subpath>')
    def serve_merchant(subpath=''):
        return send_file(os.path.join(_BASE, 'merchant_dist', 'index.html'))

    # 商家静态资源
    @app.route('/merchant/assets/<path:filename>')
    def serve_merchant_assets(filename):
        return send_file(os.path.join(_BASE, 'merchant_dist', 'assets', filename))

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

    # admin (10)
    from .controllers.admin.auth_controller import bp as admin_auth_bp
    from .controllers.admin.area_controller import bp as admin_area_bp
    from .controllers.admin.category_controller import bp as admin_category_bp
    from .controllers.admin.community_controller import bp as community_stats_bp
    from .controllers.admin.user_controller import bp as admin_user_bp
    from .controllers.admin.role_controller import bp as admin_role_bp
    from .controllers.admin.log_controller import bp as admin_log_bp
    from .controllers.admin.device_controller import bp as admin_device_bp
    from .controllers.admin.rule_controller import bp as admin_rule_bp
    from .controllers.admin.statistics_controller import bp as admin_statistics_bp
    from .controllers.admin.merchant_controller import bp as admin_merchant_bp

    # merchant (8)
    from .controllers.merchant.auth_controller import bp as merchant_auth_bp
    from .controllers.merchant.info_controller import bp as merchant_info_bp
    from .controllers.merchant.apply_controller import bp as merchant_apply_bp
    from .controllers.merchant.commodity_controller import bp as merchant_commodity_bp
    from .controllers.merchant.order_controller import bp as merchant_order_bp
    from .controllers.merchant.statistics_controller import bp as merchant_statistics_bp
    from .controllers.merchant.sub_account_controller import bp as merchant_sub_account_bp
    from .controllers.merchant.report_controller import bp as merchant_report_bp

    # 注册 blueprint
    app.register_blueprint(sms_bp, url_prefix='/api/v1/common')
    app.register_blueprint(upload_bp, url_prefix='/api/v1/common')
    app.register_blueprint(captcha_bp, url_prefix='/api/v1/common')

    app.register_blueprint(user_auth_bp, url_prefix='/api/v1/user')
    app.register_blueprint(user_info_bp, url_prefix='/api/v1/user')
    app.register_blueprint(user_point_bp, url_prefix='/api/v1/user')

    app.register_blueprint(device_auth_bp, url_prefix='/api/v1/device')
    app.register_blueprint(device_status_bp, url_prefix='/api/v1/device')

    app.register_blueprint(admin_category_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(community_stats_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_area_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_user_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_role_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_log_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_device_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_rule_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_statistics_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(admin_merchant_bp, url_prefix='/api/v1/admin')

    app.register_blueprint(merchant_auth_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_info_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_apply_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_commodity_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_order_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_statistics_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_sub_account_bp, url_prefix='/api/v1/merchant')
    app.register_blueprint(merchant_report_bp, url_prefix='/api/v1/merchant')