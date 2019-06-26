from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware
from django.middleware.csrf import get_token
from django.middleware import csrf

class CsrfViewMiddleware(DjangoCsrfViewMiddleware):
    """we use this middleware to set csrf token to
    every response, login button placed in the header
    and/or modal login menues need csrf token"""
    def __init__(self, get_response=None): # i think get_reponse is never None. If it's not another middleware it's the view, I think
        if get_response is None:
            get_response = lambda x:x
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request) # i think this simply chains all middleware
        response = self.process_response(request, response)
        return response

    def process_response(self, request, response):
        """will set csrf cookie to all responses"""
        #these two calls make the csrf token cookie to be installed
        #properly on the response, see implementation of those calls
        #to see why this works and why get_token is necessary
        get_token(request)
        return super(CsrfViewMiddleware, self).process_response(request, response)
