"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import random
import unittest

from django.test import TestCase
from django.test.client import Client

from rovserver.models import ResearchObject, AggregatedResource

class ResearchObjectsTest(TestCase):

    def test_initial_ResearchObjects(self):
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(list(ResearchObject.objects.all()), [])
        return

    def test_add_ResearchObject(self):
        ro = ResearchObject(uri="http://example.org/RO/test")
        ro.save()
        self.assertEqual(ro.uri, "http://example.org/RO/test")
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(map(str,list(ResearchObject.objects.all())), ["http://example.org/RO/test"])
        return ro

    def test_delete_ResearchObject(self):
        ro = self.test_add_ResearchObject()
        ro.delete()
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(map(str,list(ResearchObject.objects.all())), [])
        return

    def test_initial_AggregatedResource(self):
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        self.assertEqual(list(AggregatedResource.objects.all()), [])
        return

    def test_add_AggregatedResource(self):
        res_uri1 = "http://example.org/RO/test/res1"
        res_uri2 = "http://example.org/RO/test/res2"
        res_str1 = res_uri1 + " (True)"
        res_str2 = res_uri2 + " (False)"
        ro   = self.test_add_ResearchObject()
        res1 = AggregatedResource(ro=ro,uri=res_uri1,is_rdf=True)
        res1.save()
        self.assertEqual(res1.uri, res_uri1)
        self.assertEqual(len(AggregatedResource.objects.all()), 1)
        self.assertEqual(map(str,list(AggregatedResource.objects.all())), [res_str1])
        res2 = AggregatedResource(ro=ro,uri=res_uri2,is_rdf=False)
        res2.save()
        self.assertEqual(res2.uri, res_uri2)
        self.assertEqual(len(AggregatedResource.objects.all()), 2)
        self.assertEqual(map(str,list(AggregatedResource.objects.all())), [res_str1, res_str2])
        # Enumerate aggregation for ro
        ros = ResearchObject.objects.filter(uri="http://example.org/RO/test")
        self.assertEqual(len(ros), 1)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 2)
        self.assertIn(res1, ars)
        self.assertIn(res2, ars)
        return

    def test_delete_AggregatedResources(self):
        res_uri1 = "http://example.org/RO/test/res1"
        res_uri2 = "http://example.org/RO/test/res2"
        ro   = self.test_add_ResearchObject()
        res1 = AggregatedResource(ro=ro,uri=res_uri1,is_rdf=True)
        res1.save()
        res2 = AggregatedResource(ro=ro,uri=res_uri2,is_rdf=False)
        res2.save()
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(len(AggregatedResource.objects.all()), 2)
        # Delete ro
        ro.delete()
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        return


class RovServerTest(TestCase):

    def test_roverlay_home_get_html(self):
        """
        Test access to roverlay service home with HTML requested
        """
        c = Client()

        r = c.get("/rovserver/", HTTP_ACCEPT="text/html")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")

        r = c.get("/rovserver/", HTTP_ACCEPT="application/html")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")

        r = c.get("/rovserver/")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")
        return

    def test_roverlay_home_get_uri_list(self):
        """
        Test access to roverlay service home with uri-list requested
        """
        c = Client()
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, "")
        return

    def test_roverlay_home_get_error(self):
        """
        Test access to roverlay service home with unsupported type requested
        """
        c = Client()
        r = c.get("/rovserver/", HTTP_ACCEPT="application/unknown")
        self.assertEqual(r.status_code, 406)
        # self.assertEqual(r.reason_phrase, "Not Acceptable") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service error</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service error</h1>")
        self.assertRegexpMatches(r.content, "<h2>406: Not acceptable</h2>")
        return

    def test_roverlay_home_post_create_ro(self):
        """
        Test logic for creating new RO by POST to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        c = Client()
        # Create new RO
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        # self.assertEqual(r.reason_phrase, "Created") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        uri1 = r["Location"]
        self.assertRegexpMatches(uri1, "http://testserver/rovserver/ROs/[0-9[a-f]{8}/")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>New research object created</h2>")
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        # Read it back
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, uri1+"\n")
        # Create another RO
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        # self.assertEqual(r.reason_phrase, "Created") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        uri2 = r["Location"]
        self.assertRegexpMatches(uri2, "http://testserver/rovserver/ROs/[0-9[a-f]{8}/")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>New research object created</h2>")
        self.assertEqual(len(ResearchObject.objects.all()), 2)
        # Read it back
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, uri1+"\n"+uri2+"\n")
        return

    def test_roverlay_home_post_error(self):
        """
        Test POST to roverlay service home with unsupported type
        """
        c = Client()
        r = c.post("/rovserver/", data="", content_type="application/xml")
        self.assertEqual(r.status_code, 415)
        # self.assertEqual(r.reason_phrase, "Unsupported Media Type") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service error</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service error</h1>")
        self.assertRegexpMatches(r.content, "<h2>415: Unsupported Media Type</h2>")
        return

    def test_roverlay_home_ros_listed(self):
        """
        Test ROs listed on service page
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        c = Client()
        # Create new ROs
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        uri1 = r["Location"]
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        uri2 = r["Location"]
        # Read it back
        r = c.get("/rovserver/")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        def urilisting(uri):
            return """<a href="%s">%s</a>"""%(uri, uri)
        self.assertRegexpMatches(r.content, urilisting(uri1))
        self.assertRegexpMatches(r.content, urilisting(uri2))
        return

    def create_test_ro(self, uri_list=None):
        c = Client()
        base_uri = "http://example.org/resource/"
        uri_list_default = (
            [ base_uri+"res1"
            , base_uri+"res2"
            , base_uri+"res3"
            ])
        uri_list = uri_list or uri_list_default
        uri_text = "\n".join(uri_list)
        r = c.post("/rovserver/", data=uri_text, content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        ro_uri = r["Location"]
        return ro_uri

    def test_roverlay_home_post_create_aggregation(self):
        """
        Test logic for creating new RO by POST to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        c = Client()
        # Create new RO
        base_uri = "http://example.org/resource/"
        uri_list = (
            [ "# Comment at start of URI list"
            , base_uri+"res1"
            , "# Another comment"
            , base_uri+"res2"
            , ""
            , base_uri+"res3"
            ])
        ro_uri = self.create_test_ro(uri_list)
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(len(AggregatedResource.objects.all()), 3)
        # Read back RO list
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, ro_uri+"\n")
        # Check aggregated content
        ros = ResearchObject.objects.filter(uri=ro_uri)
        self.assertEqual(len(ros), 1)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 3)
        for ar in ars:
            self.assertIn(ar.uri, uri_list)
        return

    # @unittest.skip("RO GET HTML not yet implemented")
    def test_roverlay_ro_get_html(self):
        # print "********** test_roverlay_ro_get_html"
        c = Client()
        base_uri = "http://example.org/resource/"
        uri_list = (
            [ base_uri+"res1"
            , base_uri+"res2"
            , base_uri+"res3"
            ])
        ro_uri = self.create_test_ro(uri_list)
        # print "**** Created "+ro_uri
        ros = ResearchObject.objects.filter(uri=ro_uri)
        self.assertEqual(len(ros), 1)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 3)
        for ar in ars:
            self.assertIn(ar.uri, uri_list)
        # print "**** About to GET "+ro_uri
        r = c.get(ro_uri, HTTP_ACCEPT="text/html")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>Research Object %s</title>"%(ro_uri))
        # self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        # self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")
        def urilisting(uri):
            return """<a href="%s">%s</a>"""%(uri, uri)
        for uri in uri_list:
            self.assertRegexpMatches(r.content, urilisting(uri))
        return

    @unittest.skip("RO GET RDF not yet implemented")
    def test_roverlay_ro_get_rdf(self):
        assert False, "@@TODO: test not implemented"
        return

    @unittest.skip("DELETE not yet implemented")
    def test_roverlay_ro_delete(self):
        """
        Test logic for deleting RO aggregation by DELETE to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        c = Client()
        # Create new RO
        base_uri = "http://example.org/resource/"
        uri_list = (
            [ "# Comment at start of URI list"
            , base_uri+"res1"
            , base_uri+"res2"
            , base_uri+"res3"
            ])
        uri_text = "\n".join(uri_list)
        r = c.post("/rovserver/", data=uri_text, content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        ro_uri = r["Location"]
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(len(AggregatedResource.objects.all()), 3)
        # Delete RO
        r = c.delete("/rovserver/")
        self.assertEqual(r.status_code, 204)
        # Check aggregated content
        ros = ResearchObject.objects.filter(uri=ro_uri)
        self.assertEqual(len(ros), 0)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 0)
        return


        # import inspect
        # print "ATTRIBUTES:"
        # for (k,v) in inspect.getmembers(r):
        #     print "%20s  %s"%(k,repr(v))
        # print "__dict__:"
        # for k in r.__dict__:
        #     print "[%20s]  %s"%(k,repr(r.__dict__[k]))
