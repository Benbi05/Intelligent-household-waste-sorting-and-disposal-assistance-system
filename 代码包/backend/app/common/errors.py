"""全局异常处理"""
from .response import fail


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return fail(400, str(e))

    @app.errorhandler(401)
    def unauthorized(e):
        return fail(401, '未授权访问')

    @app.errorhandler(403)
    def forbidden(e):
        return fail(403, '无权限访问')

    @app.errorhandler(404)
    def not_found(e):
        return fail(404, '资源不存在')

    @app.errorhandler(429)
    def too_many_requests(e):
        return fail(429, '请求频率超限')

    @app.errorhandler(500)
    def internal_error(e):
        return fail(500, '服务器内部错误')