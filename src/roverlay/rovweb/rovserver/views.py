# Create your views here.

import random

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views import generic

from rovserver.models import ResearchObject

# Start RO IDs from random value to reduce chance of conflict when service is restarted
RO_generator = random.randint(0x00000000,0x7FFFFFFF)

class ContentNegotiationView(generic.View):
    """
    Generic view class with content negotiation decorators and generic error value methods
    """

    @staticmethod
    def accept_types(types):
        """
        Decorator to use associated function to render the indicated content types 
        """
        def decorator(func):
            def guard(self, values):
                accept_header = self.request.META.get('HTTP_ACCEPT',"default_type")
                accept_types  = [ a.split(';')[0].strip().lower() for a in accept_header.split(',') ]
                for t in types:
                    if t in accept_types:
                        return func(self, values)
                return None
            return guard
        return decorator

    @staticmethod
    def content_types(types):
        """
        Decorator to use associated function when supplied with the indicated content types 
        """
        def decorator(func):
            def guard(self, values):
                content_type = self.request.META.get('CONTENT_TYPE', "application/octet-stream")
                if content_type.split(';')[0].strip().lower() in types:
                    return func(self, values)
                return None
            return guard
        return decorator

    def get_request_uri(self):
        return self.request.build_absolute_uri()

    def error(self, values):
        """
        Default error method using errorvalues
        """
        responsebody = """
            <html>
            <head>
                <title>Error %(status)s: %(reason)s</title>
            </head>
            <body>
                <h1>Error %(status)s: %(reason)s</h1>
                <p>%(message)s</p>
            </body>
            </html>
            """ % values
        return HttpResponse(responsebody, status=values['status'])

    def errorvalues(self, status, reason, message):
        return (
            { 'status':   status
            , 'reason':   reason
            , 'message':  message%
                { 'method':         self.request.method
                , 'request_uri':    self.request.build_absolute_uri()
                , 'accept_types':   self.request.META.get('HTTP_ACCEPT',"default_type")
                , 'content_type':   self.request.META.get('CONTENT_TYPE', "application/octet-stream")
                }
            })

    def error405values(self):
        return self.errorvalues(405, "Method not allowed", 
            "Method %(method)s is not recognized for %(request_uri)s"
            )

    def error406values(self):
        return self.errorvalues(406, "Not acceptable", 
            "%(method)s returning %(accept_types)s not supported for %(request_uri)s"
            )

    def error415values(self):
        return self.errorvalues(415, "Unsupported Media Type", 
            "%(method)s with %(content_type)s not supported for %(request_uri)s"
            )

class RovServerHomeView(ContentNegotiationView):
    """
    View class to handle requests to the rovserver home URI
    """

    def generate_ro_uri(self):
        global RO_generator
        RO_generator = (RO_generator+1) & 0x7FFFFFFF
        return self.get_request_uri() + "ROs/%08x/"%RO_generator 

    @ContentNegotiationView.accept_types(["text/uri-list"])
    def render_uri_list(self, values):
        resp = HttpResponse(status=200, content_type="text/uri-list")
        for ro in values['ros']:
            resp.write(str(ro)+"\n")
        return resp

    @ContentNegotiationView.accept_types(["text/html", "application/html", "default_type"])
    def render_html(self, resultdata):
        template = loader.get_template('rovserver_home.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def error(self, values):
        template = loader.get_template('rovserver_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'])

    def get(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        resultdata = {'ros': ResearchObject.objects.all()}
        return (
            self.render_uri_list(resultdata) or
            self.render_html(resultdata) or 
            self.error(self.error406values())
            )

    @ContentNegotiationView.content_types(["text/uri-list"])
    def post_uri_list(self, values):
        # Extract URI list
        # @@TODO
        # Allocate URI
        ro_uri = self.generate_ro_uri()
        # Add to ResearchObjects model
        ro = ResearchObject(uri=ro_uri)
        ro.save()
        template = loader.get_template('rovserver_created.html')
        context = RequestContext({ 'uri': ro_uri })
        resp = HttpResponse(template.render(context), status=201)
        resp['Location'] = ro_uri
        return resp

    def post(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        return ( self.post_uri_list({}) or 
            self.error(self.error415values()) )

