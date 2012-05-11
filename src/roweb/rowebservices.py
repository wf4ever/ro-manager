import sys
import os
import logging
import StringIO

import rdflib

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from wsgiref.simple_server import make_server

if __name__ == '__main__':
    sys.path.append("..")

from uritemplate import uritemplate

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
        """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""+nl+
        """@prefix roe: <http://purl.org/ro/service/evaluate/>"""+nl+
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
              <code>/evaluate/checklist{?<cite>RO</cite>,<cite>minim</cite>,<cite>target</cite>,<cite>purpose</cite>}</code>
              Evaluates an identified research object using a checklist defined by the referenced
              <a href="https://raw.github.com/wf4ever/ro-manager/master/src/iaeval/Minim/minim.rdf">MINIM</a>
              description, selected based on the indicated target resource and purpose.
            </li>
            <li>
            ...
            </li>
          </ul>
          </p>
          <p>
          Where the URI query parameters provided are:
          <ul>
            <li><code><cite>RO</cite></code> is the %-escaped URI of a research object to be evaluated</li>
            <li><code><cite>minim</cite></code> is the %-escaped URI of a MINIM model to be evaluated</li>
            <li><code><cite>purpose</cite></code> is a purpose for which the evaluation is performed (e.g. "Complete", "Runnable", etc.)
                The recognised values for this parameter will depend on what is defined by the MINIM model used.</li>
            <li><code><cite>target</cite></code> is the %-escaped URI of a target resource to which the purpose is applied</li>
          </ul>
          </p>
        </body>
        </html>\n""")
    return Response(sd, content_type="text/html", vary=['accept'])

def evaluate(request):
    graph = rdflib.Graph()
    rgstr = StringIO.StringIO(
        """@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix result:     <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
        @prefix minim:      <http://purl.org/minim/minim#> .
        <http://sandbox.example.org/ROs/myro>
          minim:testedConstraint   <http://another.example.com/minim/repeatable.rdf#runnable-RO-constraint> ;
          minim:testedPurpose      "Runnable" ;
          minim:testedTarget       <http://sandbox.example.org/ROs/myro> ;
          minim:fullySatisfies     <http://another.example.com/minim/repeatable.rdf#runnable-RO-checklist> ;
          minim:nominallySatisfies <http://another.example.com/minim/repeatable.rdf#runnable-RO-checklist> ;
          minim:minimallySatisfies <http://another.example.com/minim/repeatable.rdf#runnable-RO-checklist> ;
          # minim:missingMust      ... (none)
          # minim:missingShould    ... (none)
          # minim:missingMay       ... (none)
          minim:satisfied
            [ minim:tryRule <http://another.example.com/minim/repeatable.rdf#environment-software/lpod-show> ],
            [ minim:tryRule <http://another.example.com/minim/repeatable.rdf#environment-software/python> ],
            [ minim:tryRule <http://another.example.com/minim/repeatable.rdf#isPresent/workflow-instance>],
            [ minim:tryRule <http://another.example.com/minim/repeatable.rdf#isPresent/workflow-inputfiles> ;
              result:binding
                [ result:variable "wf" ; result:value "http://sandbox.example.org/ROs/myro/docs/mkjson.sh" ],
                [ result:variable "wi" ; result:value "GZZzLCkR38" ],
                [ result:variable "if" ; result:value "http://sandbox.example.org/ROs/myro/data/UserRequirements-gen.ods" ]
            ] .
        """)
    graph.parse(rgstr, format="turtle")
    return graph

@view_config(route_name='evaluate', request_method='GET', accept='text/turtle')
def evaluate_turtle(request):
    resultgraph = evaluate(request)
    return Response(resultgraph.serialize(format='turtle'), content_type="text/turtle", vary=['accept'])

@view_config(route_name='evaluate', request_method='GET', accept='application/rdf+xml')
def evaluate_rdf(request):
    resultgraph = evaluate(request)
    return Response(resultgraph.serialize(format='pretty-xml'), content_type="application/rdf+xml", vary=['accept'])

@view_config(route_name='template', request_method='POST')
def expand_uri_template(request):
    tp = request.json_body
    uri = uritemplate.expand(tp['template'], tp['params'])
    return Response(uri+"\n", content_type="text/plain")

if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    # configuration setup
    config = Configurator(settings=settings)
    config.add_route(name='service', pattern='/')
    config.add_route(name='evaluate', pattern='/evaluate/checklist')
    config.add_route(name='template', pattern='/uritemplate')
    config.add_route(name='hello',   pattern='/hello/{name}')
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

