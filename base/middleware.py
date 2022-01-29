import time


class PerformanceStatistics:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.performance_statistics_start_time = time.time()
        response = self.get_response(request)
        total = time.time() - request.performance_statistics_start_time

        # Add the header.
        response["PS-running-time"] = f"{int(total * 1000)} ms"
        response["PS-request-ip"] = self.get_client_ip(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_list = x_forwarded_for.split(',')
            ip = ip_list
        else:
            ip = request.META.get('REMOTE_ADDR', None)
        return ip

class BeforeStatsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.server_response_start_time = time.time()
        response = self.get_response(request)
        return response


class FinallyStatsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        total = time.time() - request.server_response_start_time

        # Add the header.
        response["server-response-total-time"] = f"{int(total * 1000)} ms"

        return response
