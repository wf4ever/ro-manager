import sys
import os
import logging
import StringIO
import json
import urllib
import urlparse

import rdflib

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from wsgiref.simple_server import make_server

if __name__ == '__main__':
    sys.path.append("..")
    logging.basicConfig(level=logging.INFO)

from uritemplate import uritemplate

from rocommand.ro_namespaces import RDF, RDFS
from rocommand.ro_annotation import annotationTypes, annotationPrefixes
from rocommand.ro_metadata   import ro_metadata

from iaeval          import ro_eval_minim
from iaeval.ro_minim import MINIM, RESULT

import RdfReport
import TrafficLightReports

log  = logging.getLogger(__file__)
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
        """    <roe:trafficlight_json>/evaluate/trafficlight_json{?RO,minim,target,purpose}</roe:trafficlight_json>"""+nl+
        """    <roe:trafficlight_html>/evaluate/trafficlight_html{?RO,minim,target,purpose}</roe:trafficlight_html>"""+nl+
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
        """<> roe:checklist "/evaluate/checklist{?RO,minim,target,purpose}" ."""+nl+
        """<> roe:trafficlight_json "/evaluate/trafficlight_json{?RO,minim,target,purpose}" ."""+nl+
        """<> roe:trafficlight_html "/evaluate/trafficlight_html{?RO,minim,target,purpose}" ."""+nl+
        ""
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
          This web server offers services to evaluate Research Objects.
          Dereferencing the URI of this page with content negotiation for RDF/XML or Turtle
          will return a service description document that contains URI templates
          (<a href="http://tools.ietf.org/html/rfc6570">RFC 6570</a>) for each of the services 
          described below.
          </p>
          <p>
          The services offered are:
          <ul>
            <li><code>/evaluate/checklist{?<cite>RO</cite>,<cite>minim</cite>,<cite>target</cite>,<cite>purpose</cite>}</code>
              This is the primaruy checklist evaluation service.
              It evaluates an identified research object using a checklist defined by the referenced
              <a href="http://purl.org/minim/minim">Minim</a>
              description, selected based on the indicated target resource and purpose,
              and returns the result as an RDF graph in a selected format using the
              <a href="http://purl.org/minim/results">Minim-results</a> vocabulary.
              Further descriptions of these can be found on 
              <a href="https://github.com/wf4ever/ro-manager/blob/master/Minim/Minim-description.md">GitHub</a>. 
            </li>
            <li><code>/evaluate/trafficlight_json{?<cite>RO</cite>,<cite>minim</cite>,<cite>target</cite>,<cite>purpose</cite>}</code>
              This is a layered checklist result presentation service that 
              evaluates an identified research object using a checklist defined by the referenced
              <a href="http://purl.org/minim/minim">Minim</a>
              description, selected based on the indicated target resource and purpose.
              The result of the evaluation is then processed into JSON data designed to drive
              a "traffic-light" display of the conformance of the RO with the checklist requirements.
            </li>
            <li><code>/evaluate/trafficlight_html{?<cite>RO</cite>,<cite>minim</cite>,<cite>target</cite>,<cite>purpose</cite>}</code>
              This is another layered checklist result presentation service that 
              evaluates an identified research object using a checklist defined by the referenced
              <a href="http://purl.org/minim/minim">Minim</a>
              description, selected based on the indicated target resource and purpose.
              The result of the evaluation is then processed into HTML that presents a "traffic-light"
              display of the conformance of the RO with the checklist requirements, summarizing the overall
              result and which of the individual checklist items were satisfied or not satisfied.
            </li>
          </ul>
          </p>
          <p>
          The URI query parameters provided are:
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

def real_evaluate(request):
    # From: http://tools.ietf.org/html/rfc3986#section-2.1
    # gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    # sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
    #              / "*" / "+" / "," / ";" / "="
    quotesafe = ":/?#[]@!$&'()*+,;=" + "%"
    # isolate parameters (keep invalid URI characters %-encoded)
    RO      = urllib.quote(request.params["RO"], quotesafe)
    minim   = urllib.quote(request.params["minim"], quotesafe)
    target  = urllib.quote(request.params.get("target","."), quotesafe)
    purpose = request.params["purpose"]
    log.info("Evaluate RO %s, minim %s, target %s, purpose %s"%(RO,minim,target,purpose))
    # create rometa object
    # @@TODO: use proper configuration and credentials
    ROparse   = urlparse.urlparse(RO)
    rosrs_uri = (ROparse.scheme or "http") + "://" + (ROparse.netloc or "localhost:8000") + "/"
    ro_config = {
        "annotationTypes":      annotationTypes,
        "annotationPrefixes":   annotationPrefixes,
        "rosrs_uri":            rosrs_uri,
        #"rosrs_uri":            target,
        #"rosrs_uri":            "http://sandbox.wf4ever-project.org/rodl/ROs/",
        #"rosrs_access_token":   "ac14dd1a-ab59-40ec-b510-ffdb01a85473",
        "rosrs_access_token":   None,
        }
    rometa = ro_metadata(ro_config, RO)
    log.info("rometa.rouri: %s"%(rometa.rouri) )
    # invoke evaluation service
    (graph, evalresult) = ro_eval_minim.evaluate(rometa, minim, target, purpose)
    log.debug("evaluate:results: \n"+json.dumps(evalresult, indent=2))
    # Assemble graph of results
    graph =  ro_eval_minim.evalResultGraph(graph, evalresult)
    return graph

def fake_evaluate(request):
    graph = rdflib.Graph()
    rgstr = StringIO.StringIO(
        """@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix result:     <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
        @prefix minim:      <http://purl.org/minim/minim#> .
        <http://sandbox.example.org/ROs/myro>
          minim:testedChecklist   <http://another.example.com/minim/repeatable.rdf#runnable-RO-constraint> ;
          minim:testedPurpose      "Runnable" ;
          minim:testedTarget       <http://sandbox.example.org/ROs/myro> ;
          minim:fullySatisfies     <http://another.example.com/minim/repeatable.rdf#runnable-RO-checklist> ;
          minim:nominallySatisfies <http://another.example.com/minim/repeatable.rdf#runnable-RO-checklist> ;
          minim:minimallySatisfies <http://another.example.com/minim/repeatable.rdf#runnable-RO-checklist> ;
          # minim:missingMust      ... (none)
          # minim:missingShould    ... (none)
          # minim:missingMay       ... (none)
          minim:satisfied
            [ minim:tryRequirement <http://another.example.com/minim/repeatable.rdf#environment-software/lpod-show> ],
            [ minim:tryRequirement <http://another.example.com/minim/repeatable.rdf#environment-software/python> ],
            [ minim:tryRequirement <http://another.example.com/minim/repeatable.rdf#isPresent/workflow-instance>],
            [ minim:tryRequirement <http://another.example.com/minim/repeatable.rdf#isPresent/workflow-inputfiles> ;
              result:binding
                [ result:variable "wf" ; result:value "http://sandbox.example.org/ROs/myro/docs/mkjson.sh" ],
                [ result:variable "wi" ; result:value "GZZzLCkR38" ],
                [ result:variable "if" ; result:value "http://sandbox.example.org/ROs/myro/data/UserRequirements-gen.ods" ]
            ] .
        """)
    graph.parse(rgstr, format="turtle")
    return graph

evaluate = real_evaluate

@view_config(route_name='evaluate', request_method='GET', accept='text/html')
def evaluate_html(request):
    """
    Return details of request as HTML page
    """
    r1 = request.params
    # NestedMultiDict([(u'RO', u'http://sandbox.example.org/ROs/myro'), 
    #                  (u'minim', u'http://another.example.com/minim/repeatable.rdf'),
    #                  (u'purpose', u'Runnable')])
    r2 = ("""<h1>Evaluate HTML</h1>
        <h2>Multidict</h2>
        <pre>
        """+repr(r1)+"""
        </pre>
        <h2>Values</h2>
        <p>RO:      """+request.params["RO"]+"""</p>
        <p>minim:   """+request.params["minim"]+"""</p>
        <p>target:  """+request.params.get("target",".")+"""</p>
        <p>purpose: """+request.params["purpose"]+"""</p>
        """)
    return Response(r2, content_type="text/html", vary=['accept'])

@view_config(route_name='evaluate', request_method='GET', accept='text/turtle')
def evaluate_turtle(request):
    """
    Return checklist evaluation as RDF/Turtle
    """
    resultgraph = evaluate(request)
    return Response(resultgraph.serialize(format='turtle'), content_type="text/turtle", vary=['accept'])

@view_config(route_name='evaluate', request_method='GET', accept='application/rdf+xml')
def evaluate_rdf(request):
    """
    Return checklist evaluation as RDF/XML
    """
    resultgraph = evaluate(request)
    return Response(resultgraph.serialize(format='pretty-xml'),
                    content_type="application/rdf+xml", vary=['accept'])

### @view_config(route_name='trafficlight', request_method='GET', accept='application/json')
@view_config(route_name='trafficlight_json', request_method='GET')
def evaluate_trafficlight_json(request):
    """
    Return JSON data for trafficlight display of checklist evaluation
    
    Request parameters as as for checklist evaluation.
    """
    resultgraph = evaluate(request)
    outstr      = StringIO.StringIO()
    RdfReport.generate_report(
        TrafficLightReports.EvalChecklistJson, resultgraph, {}, outstr, RdfReport.escape_json)
    return Response(outstr.getvalue(), content_type="application/json", vary=['accept'])

### @view_config(route_name='trafficlight', request_method='GET', accept='text/html')
@view_config(route_name='trafficlight_html', request_method='GET')
def evaluate_trafficlight_html(request):
    """
    Return HTML page for trafficlight display of checklist evaluation
    
    Request parameters as as for checklist evaluation.
    """
    resultgraph = evaluate(request)
    outstr      = StringIO.StringIO()
    RdfReport.generate_report(
        TrafficLightReports.EvalChecklistHtml, resultgraph, {}, outstr, RdfReport.escape_html)
    return Response(outstr.getvalue(), content_type="text/html", vary=['accept'])

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
    config.add_route(name='trafficlight_json', pattern='/evaluate/trafficlight_json')
    config.add_route(name='trafficlight_html', pattern='/evaluate/trafficlight_html')
    config.add_route(name='template', pattern='/uritemplate')
    config.add_route(name='hello',   pattern='/hello/{name}')
    config.add_static_view(name='evaluate/images', path='images')
    config.add_static_view(name='evaluate/css',    path='css')
    config.add_static_view(name='evaluate/js',     path='js')
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

