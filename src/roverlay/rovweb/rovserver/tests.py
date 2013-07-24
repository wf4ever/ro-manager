"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import random

from django.test import TestCase
from django.test.client import Client

from rovserver.models import ResearchObject

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

        # import inspect
        # print "ATTRIBUTES:"
        # for (k,v) in inspect.getmembers(r):
        #     print "%20s  %s"%(k,repr(v))
        # print "__dict__:"
        # for k in r.__dict__:
        #     print "[%20s]  %s"%(k,repr(r.__dict__[k]))
