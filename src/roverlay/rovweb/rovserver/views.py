# Create your views here.

import random

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views import generic

from rovserver.ContentNegotiationView import ContentNegotiationView

from rovserver.models import ResearchObject, AggregatedResource

# Start RO IDs from random value to reduce chance of conflict when service is restarted
RO_generator = random.randint(0x00000000,0x7FFFFFFF)

class RovServerHomeView(ContentNegotiationView):
    """
    View class to handle requests to the rovserver home URI
    """

    def error(self, values):
        template = loader.get_template('rovserver_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'])

    # GET

    @ContentNegotiationView.accept_types(["text/uri-list"])
    def render_uri_list(self, resultdata):
        resp = HttpResponse(status=200, content_type="text/uri-list")
        for ro in resultdata['rouris']:
            resp.write(str(ro)+"\n")
        return resp

    @ContentNegotiationView.accept_types(["text/html", "application/html", "default_type"])
    def render_html(self, resultdata):
        template = loader.get_template('rovserver_home.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        resultdata = {'rouris': ResearchObject.objects.all()}
        return (
            self.render_uri_list(resultdata) or
            self.render_html(resultdata) or 
            self.error(self.error406values())
            )

    # POST

    def generate_ro_uri(self):
        global RO_generator
        RO_generator = (RO_generator+1) & 0x7FFFFFFF
        return self.get_request_uri() + "ROs/%08x/"%RO_generator 

    def make_resource(self, ro, uri):
        # @@TODO: test URI content type
        return AggregatedResource(ro=ro, uri=uri, is_rdf=False)

    @ContentNegotiationView.content_types(["text/uri-list"])
    def post_uri_list(self, values):
        # Extract URI list
        def hascontent(s):
            return s and (not s.startswith("#"))
        uri_list = filter(hascontent, unicode(self.request.body).splitlines())
        # Allocate URI
        ro_uri = self.generate_ro_uri()
        # Add to ResearchObjects model
        ro = ResearchObject(uri=ro_uri)
        ro.save()
        # Add aggregated URIs
        for u in uri_list:
            r = self.make_resource(ro, u)
            r.save()
            # print "resource: uri %s, ro %s, rdf %s "%(r.uri, r.ro.uri, r.is_rdf)
        # Assemble and return response
        template = loader.get_template('rovserver_created.html')
        context = RequestContext({ 'uri': ro_uri })
        resp = HttpResponse(template.render(context), status=201)
        resp['Location'] = ro_uri
        return resp

    def post(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        return ( self.post_uri_list({}) or 
            self.error(self.error415values()) )


class ResearchObjectView(ContentNegotiationView):
    """
    View class to handle requests to a research obect URI
    """

    @ContentNegotiationView.accept_types(["application/rdf+xml", "text/turtle", ""])
    def render_rdf(self, resultdata):
        resp = HttpResponse(status=200, content_type=resultdata["accept_type"])
        raise Exception("@@TODO: unimplemented")
        return resp

    @ContentNegotiationView.accept_types(["text/html", "application/html", "default_type"])
    def render_html(self, resultdata):
        template = loader.get_template('research_object_home.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request, roslug):
        # print "RO slug: %s"%(roslug)
        self.request = request      # For clarity: generic.View does this anyway
        ro_uri       = self.get_request_uri()
        ro           = ResearchObject.objects.get(uri=ro_uri)
        # print "RO URI: %s (%s)"%(ro_uri, ro.uri)
        ro_resources = AggregatedResource.objects.filter(ro=ro)
        # for res in ro_resources:
        #     print "ro_resource: %s"%(res)
        resultdata = (
            { 'ro_uri':         ro_uri
            , 'ro_resources':   ro_resources
            })
        return (
            self.render_rdf(resultdata) or
            self.render_html(resultdata) or 
            self.error(self.error406values())
            )

    def delete(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        raise Exception("@@TODO: unimplemented")
        return self.error(self.error405values())

# End.

