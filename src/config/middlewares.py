import logging

logger = logging.getLogger(__name__)
print(__name__)

class SimpleLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        logger.info(
            {
                "method": request.method,
                "status_code": response.status_code,
                "message": "hello world",
            }
        )
        return response
