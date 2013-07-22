# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader

def index1(request):
    responseHTML = """
        <h1>roverlay service</h1>
        <p>
          GET returns a list of currently-defined ROs.
        </p>
        <p>
          POST acepts a list of URIs, creates a new Overlay RO, and returns a "201 Created"
          response with a Location header giving the URI of the newly created RO.
        </p>
        <p>
          See also: <a href="https://github.com/wf4ever/ro-manager/blob/develop/src/roverlay/roverlay.md">ro-manager/src/roverlay/roverlay.md in GitHub</a>.
        </p>
        """
    return HttpResponse(responseHTML)

def accept_html(request):
    return accept_types(request, ["application/html", "text/html"])

def accept_types(request, types):
    acc = [ a.split(';')[0].strip().lower() for a in request.META['HTTP_ACCEPT'].split(',') ]
    for t in types:
        if t in acc: return t
    return None

def index(request):
    if request.method == "GET" and accept_html(request):
        template = loader.get_template('rovserver_home.html')
        context = RequestContext(request, {})
        resp = HttpResponse(template.render(context))
    elif request.method == "GET" and accept_types(request, ["text/uri-list"]):
        template = loader.get_template('rovserver_error.html')
        context = RequestContext(request, 
            { 'status': 501
            , 'reason': "Not implemented"
            , 'message': "GET for text/uri-list not currently implemented"
            })
        resp = HttpResponse(template.render(context), status=501)
    else:
        template = loader.get_template('rovserver_error.html')
        context = RequestContext(request, 
            { 'status': 501
            , 'reason': "Not implemented"
            , 'message': "Methods other than GET not currenmtly implemented for this resource"
            })
        resp = HttpResponse(template.render(context), status=501)
    return resp
