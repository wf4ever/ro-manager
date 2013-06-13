from urlparse import urljoin
from ROSRS_Session import ROSRS_Session
import logging
import json
from ro_utils import parse_job, EvoType
import sys, select
import time

log = logging.getLogger(__name__)

def copy_operation(options, args, ro_type):
    print options["rosrs_uri"]
    options["rosrs_access_token"]
    rosrs = ROSRS_Session(options["rosrs_uri"], options["rosrs_access_token"])
    service_uri = urljoin(options["rosrs_uri"], "../evo/copy/")
    body = {
        'copyfrom': args[2],
        'type': ro_type,
        'finalize': ( "%s" % options['freeze']).lower()
    }
    body = json.dumps(body)
    reqheaders = {
        'Slug' : args[3]
    }
    response = rosrs.doRequest(uripath=service_uri, method="POST", body=body, ctype="application/json", reqheaders=reqheaders)
    if response[0] != 201:
        return handle_copy_error(options, rosrs, response, ro_type)
    if not options["asynchronous"] and not options["synchronous"]:
        return handle_synchronous_copy_operation_with_esc_option(options, rosrs, response, ro_type)
    if options["asynchronous"]:
        return handle_asynchronous_copy_operation(options, rosrs, response, ro_type)
    if options["synchronous"]:
        return handle_synchronous_copy_operation(options, rosrs, response, ro_type)
    return 0
    
def handle_copy_error(options, rosrs, response, type):
    (status, reason, headers, data) = response
    if type == "SNAPSHOT":
        print "Snapshot isn't created"
    else:
        print "Archive isn't created"
    print "Status: %s" % status
    print "Reason: %s" % reason
    return 1

def handle_asynchronous_copy_operation(options, rosrs, response, type):
    (status, reason, headers, data) = response
    job_location = get_location(headers)  
    (job_status, target_id) = parse_job(rosrs,job_location)
    if type == "SNAPSHOT":
        print "Snapshot is processed"
    else:
        print "Archive if processed"
    print "Response Status: %s" % status
    print "Response Reason: %s" % reason
    print "Job Status: %s" % job_status
    print "Job URI: %s" % job_location
    print "Target Name: %s" % target_id
    print "Target URI: %s" % urljoin(options["rosrs_uri"],target_id)
    return 0

def handle_synchronous_copy_operation(options, rosrs, response, typ):
    (status, reason, headers, data) = response
    job_location = get_location(headers)
    print "Job URI: %s" % job_location
    print "Job Status: %s" % parse_job(rosrs, job_location)[0]
    while print_job_status(parse_job(rosrs, job_location), options, True):
        time.sleep(1)
    return 0

def print_job_status(args, options, verbose, force = False):
    if (options["verbose"] and verbose) or force:
        print "Target Name: %s" % args[1]
        print "Job Status: %s" % args[0]
    if args[0] != "RUNNING" or force:
        if not options["verbose"]:
            print "Job Status: %s" % args[0]    
        print "Target URI: %s" % urljoin(options["rosrs_uri"],args[1],)
    return args[0] == "RUNNING"

def handle_synchronous_copy_operation_with_esc_option(options, rosrs, response, type):
    (status, reason, headers, data) = response
    job_location = get_location(headers)
    if type == "SNAPSHOT" :
        print "Snapshot is processed"
    else:
        print "Archive is processed"
    print "If you don't want to wait until the operation is finished press [ENTER]"
    print "Job URI: %s" % job_location
    i, o, e = select.select( [sys.stdin], [], [], 10 )
    while print_job_status(parse_job(rosrs, job_location), options, False):
        if (i) and "" == sys.stdin.readline().strip():
            print "Job URI: %s" % job_location
            print_job_status(parse_job(rosrs, job_location), options, True, True)
            break
    return 0
    
def freeze(options, args):
    rosrs = ROSRS_Session(options["rosrs_uri"], options["rosrs_access_token"])
    service_uri = urljoin(options["rosrs_uri"], "../evo/finalize/")
    body = {
        'target': args[2],
    }
    body = json.dumps(body)
    reqheaders = {}
    (status, reason, headers, data) = response = rosrs.doRequest(uripath=service_uri, method="POST", body=body, ctype="application/json", reqheaders=reqheaders)
    if "location" in headers:
        while print_job_status(parse_job(rosrs, headers['location']), options, True):
            time.sleep(1)
        print "freeze operation finished successfully"
        return 0
    else:
        print status
        print reason
        print headers
        print data
        print "Given URI isn't correct"
        return -1
    
#helpers
def get_location(headers):
    for elem in headers["_headerlist"]:
        if len(elem)==2 and elem[0]=="location":
            return elem[1]