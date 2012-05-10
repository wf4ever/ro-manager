import os
import logging

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config

from wsgiref.simple_server import make_server

logging.basicConfig()
log = logging.getLogger(__file__)
here = os.path.dirname(os.path.abspath(__file__))

@view_config(route_name='hello', request_method='GET')
def hello(request):
    #return Response(repr(request.host))
    #return Response(repr(request.current_route_url()))
    #return Response(repr(request.__dict__))
    dict = {'host': request.host, 'server': request.server_name}
    dict.update(request.matchdict)
    return Response('Hello %(name)s! From %(host)s or %(server)s' % dict)

@view_config(route_name='service', request_method='GET', accept='application/rdf+xml')
def service_rdf_xml(request):
    nl = '\n'
    sd = (
        """<?xml version="1.0"?>"""+nl+
        """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:roe="http://purl.org/ro/service/evaluate/">"""+nl+
        """  <rdf:Description rdf:about="">"""+nl+
        """    <roe:checklist>/evaluate/checklist{?RO,minim,target,purpose}</roe:checklist>"""+nl+
        """  </rdf:Description>"""+nl+
        """</rdf:RDF>"""+nl
        )
    return Response(sd, content_type="application/rdf+xml", vary=['accept'])

@view_config(route_name='service', request_method='GET', accept='text/turtle')
def service_turtle(request):
    nl = '\n'
    sd = (
        """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""+nl+
        """PREFIX roe: <http://purl.org/ro/service/evaluate/>"""+nl+
        """<> roe:checklist "/evaluate/checklist{?RO,minim,target,purpose}" ."""+nl
        )
    return Response(sd, content_type="text/turtle", vary=['accept'])

@view_config(route_name='service', request_method='GET', accept="text/html")
def service_html(request):
    nl = '\n'
    sd = ("""
        <html>
        <head>
          <title>Research Object services</title>
        </head>
        <body>
          <h1>Research Object services</h1>
          <p>
          This web site offers services to evaluate Research Objects.  The services offered are:
          <ul>
            <li>
              <code>/evaluate/checklist{?RO,minim,target,purpose}</code>
              Evaluates a identified research object using a checklist defined by the referenced
              <a href="https://raw.github.com/wf4ever/ro-manager/master/src/iaeval/Minim/minim.rdf">MINIM</a>
              description, selected based on the indicated target resource and purpose.
            </li>
            <li>
            ...
            </li>
          </ul>
          </p>
          <p>
          Where the URI query paramneters provided are:
          <ul>
            <li><code>RO</code> is the %-escaped URI of a research object to be evaluated</li>
            <li><code>minim</code> is the %-escaped URI of a MINIM model to be evaluated</li>
            <li><code>purpose</code> is a purpose for which the evaluation is performed (e.g. "Complete", "Runnable", etc.)
                The recognised values for this parameter will depend on what is defined by the MIONIM model used.</li>
            <li><code>target</code> is the %-escaped URI of a target resource to which the purpose is applied</li>
          </ul>
          </p>
        </body>
        </html>
        """)
    return Response(sd, content_type="text/html", vary=['accept'])

if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    # configuration setup
    config = Configurator(settings=settings)
    config.add_route(name='service', pattern='/')
    config.add_route(name='hello',   pattern='/hello/{name}')
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

