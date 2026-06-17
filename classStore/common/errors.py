import logging

from werkzeug.exceptions import HTTPException

from classStore.common.response import fail


def register_error_handlers(app):
    logger = logging.getLogger('flask.errors')

    @app.errorhandler(404)
    def not_found(e):
        return fail('Not Found', http_status=404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return fail('Method Not Allowed', http_status=405)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return fail(e.description or e.name, http_status=e.code)

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception('Unhandled exception: %s', e)
        return fail('Internal Server Error', http_status=500)
