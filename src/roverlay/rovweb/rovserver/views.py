# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader

from rovserver.models import ResearchObject

def accept_html(request):
    return accept_types(request, ["application/html", "text/html", "default_type"])

def accept_types(request, types):
    accept_header = request.META.get('HTTP_ACCEPT',"default_type")
    acc = [ a.split(';')[0].strip().lower() for a in accept_header.split(',') ]
    for t in types:
        if t in acc: return t
    return None

def index(request):
    if request.method == "GET" and accept_html(request):
        template = loader.get_template('rovserver_home.html')
        context = RequestContext(request, {})
        resp = HttpResponse(template.render(context))
    elif request.method == "GET" and accept_types(request, ["text/uri-list"]):
        resp = HttpResponse(status=200, content_type="text/uri-list")
        for ro in ResearchObject.objects.all():
            resp.write(str(ro)+"\n")
    elif request.method == "GET":
        template = loader.get_template('rovserver_error.html')
        context = RequestContext(request, 
            { 'status': 406
            , 'reason': "Not acceptable"
            , 'message': "GET for %s not supported"%(request.META.get('HTTP_ACCEPT',"default_type"))
            })
        resp = HttpResponse(template.render(context), status=501)
    else:
        template = loader.get_template('rovserver_error.html')
        context = RequestContext(request, 
            { 'status': 501
            , 'reason': "Not implemented"
            , 'message': "Methods other than GET not currently implemented for this resource"
            })
        resp = HttpResponse(template.render(context), status=501)
    return resp

