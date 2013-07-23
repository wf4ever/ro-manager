# Create your views here.

import random

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views import generic

from rovserver.models import ResearchObject

# Start RO IDs from random value to reduce chance of conflict when service is restarted
RO_generator = random.randint(0x00000000,0x7FFFFFFF)

# def get_request_uri(request):
#     return request.build_absolute_uri()

# def get_request_content_type(request):
#     return request.META.get('CONTENT_TYPE', "application/octet-stream")

# def accept_html(request):
#     return accept_types(request, ["application/html", "text/html", "default_type"])

# def accept_types(request, types):
#     accept_header = request.META.get('HTTP_ACCEPT',"default_type")
#     acc = [ a.split(';')[0].strip().lower() for a in accept_header.split(',') ]
#     for t in types:
#         if t in acc: return t
#     return None

# def content_types(request, types):
#     ct = get_request_content_type(request).split(';')[0].strip().lower()
#     if ct in types: return ct
#     return None

# def generate_ro_uri(request):
#     global RO_generator
#     RO_generator = (RO_generator+1) & 0x7FFFFFFF
#     return get_request_uri(request) + "ROs/%08x/"%RO_generator 

# def index(request):
#     if request.method == "GET" and accept_html(request):
#         template = loader.get_template('rovserver_home.html')
#         context = RequestContext(request, {})
#         resp = HttpResponse(template.render(context))
#     elif request.method == "GET" and accept_types(request, ["text/uri-list"]):
#         resp = HttpResponse(status=200, content_type="text/uri-list")
#         for ro in ResearchObject.objects.all():
#             resp.write(str(ro)+"\n")
#     elif request.method == "GET":
#         template = loader.get_template('rovserver_error.html')
#         context = RequestContext(request, 
#             { 'status': 406
#             , 'reason': "Not acceptable"
#             , 'message': "GET for %s not supported"%(request.META.get('HTTP_ACCEPT',"default_type"))
#             })
#         resp = HttpResponse(template.render(context), status=406)
#     elif request.method == "POST" and content_types(request, ["text/uri-list"]):
#         # Create new RO
#         # Allocate URI
#         ro_uri = generate_ro_uri(request)
#         # Add to ResearchObjects model
#         ro = ResearchObject(uri=ro_uri)
#         ro.save()
#         template = loader.get_template('rovserver_created.html')
#         context = RequestContext(request, { 'uri': ro_uri })
#         resp = HttpResponse(template.render(context), status=201)
#         resp['Location'] = ro_uri
#     elif request.method == "POST":
#         template = loader.get_template('rovserver_error.html')
#         context = RequestContext(request, 
#             { 'status': 415
#             , 'reason': "Unsupported Media Type"
#             , 'message': "POST with %s not supported"%(get_request_content_type(request))
#             })
#         resp = HttpResponse(template.render(context), status=415)
#     else:
#         template = loader.get_template('rovserver_error.html')
#         context = RequestContext(request, 
#             { 'status': 501
#             , 'reason': "Not implemented"
#             , 'message': "Methods other than GET and POST not currently implemented for this resource"
#             })
#         resp = HttpResponse(template.render(context), status=501)
#     return resp

class RovServerHomeView(generic.View):

    # Generic content negotiation and filtering support

    def accept_types(types):
        """
        Decorator to use associated function to render the indicated content types 
        """
        def decorator(func):
            def guard(self, request, values):
                accept_header = request.META.get('HTTP_ACCEPT',"default_type")
                accept_types  = [ a.split(';')[0].strip().lower() for a in accept_header.split(',') ]
                for t in types:
                    if t in accept_types:
                        return func(self, request, values)
                return None
            return guard
        return decorator

    def content_types(types):
        """
        Decorator to use associated function when supplied with the indicated content types 
        """
        def decorator(func):
            def guard(self, request, values):
                content_type = request.META.get('CONTENT_TYPE', "application/octet-stream")
                if content_type.split(';')[0].strip().lower() in types:
                    return func(self, request, values)
                return None
            return guard
        return decorator

    def error(self, request, values):
        template = loader.get_template('rovserver_error.html')
        context = RequestContext(request, values)
        return HttpResponse(template.render(context), status=values['status'])

    def errorvalues(self, request, status, reason, message):
        return (
            { 'status':   status
            , 'reason':   reason
            , 'message':  message%
                { 'method':         request.method
                , 'request_uri':    request.build_absolute_uri()
                , 'accept_types':   request.META.get('HTTP_ACCEPT',"default_type")
                , 'content_type':   request.META.get('CONTENT_TYPE', "application/octet-stream")
                }
            })

    def error405values(self, request):
        return self.errorvalues(request, 405, "Method not allowed", 
            "Method %(method)s is not recognized for %(request_uri)s"
            )

    def error406values(self, request):
        return self.errorvalues(request, 406, "Not acceptable", 
            "%(method)s returning %(accept_types)s not supported for %(request_uri)s"
            )

    def error415values(self, request):
        return self.errorvalues(request, 415, "Unsupported Media Type", 
            "%(method)s with %(content_type)s not supported for %(request_uri)s"
            )

    def get_request_uri(self, request):
        return request.build_absolute_uri()

    # Specific handler methods

    def generate_ro_uri(self, request):
        global RO_generator
        RO_generator = (RO_generator+1) & 0x7FFFFFFF
        return self.get_request_uri(request) + "ROs/%08x/"%RO_generator 

    @accept_types(["text/uri-list"])
    def render_uri_list(self, request, values):
        resp = HttpResponse(status=200, content_type="text/uri-list")
        for ro in values['ros']:
            resp.write(str(ro)+"\n")
        return resp

    @accept_types(["text/html", "application/html", "default_type"])
    def render_html(self, request, resultdata):
        template = loader.get_template('rovserver_home.html')
        context = RequestContext(request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request):
        resultdata = {'ros': ResearchObject.objects.all()}
        return (
            self.render_uri_list(request, resultdata) or
            self.render_html(request, resultdata) or 
            self.error(request, self.error406values(request))
            )

    @content_types(["text/uri-list"])
    def post_uri_list(self, request, values):
        # Allocate URI
        ro_uri = self.generate_ro_uri(request)
        # Add to ResearchObjects model
        ro = ResearchObject(uri=ro_uri)
        ro.save()
        template = loader.get_template('rovserver_created.html')
        context = RequestContext(request, { 'uri': ro_uri })
        resp = HttpResponse(template.render(context), status=201)
        resp['Location'] = ro_uri
        return resp

    def post(self, request):
        return ( self.post_uri_list(request, {}) or 
            self.error(request, self.error415values(request)) )


    # def view(request):
    #     if request.method == "GET":
    #         return get(request)
    #     elif request.method == "POST":
    #         return ( post(request, {}) or error(request, error415values(request)) )
    #     else:
    #         return error(request, error405values(request))

    # def as_view():
    #     # Return view function
    #     return view

