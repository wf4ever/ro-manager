"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

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

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_roverlay_home_get_html(self):
        """
        Test access to roverlay service home with HTML requested
        """
        c = Client()

        r = c.get("/rovserver/", HTTP_ACCEPT="text/html")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")

        r = c.get("/rovserver/", HTTP_ACCEPT="application/html")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")

        r = c.get("/rovserver/")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        return

    def test_roverlay_home_get_uri_list(self):
        """
        Test access to roverlay service home with uri-list requested
        """
        c = Client()
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        # print "Content: '"+r.content+"'"
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, "")
        return




        # import inspect
        # print "ATTRIBUTES:"
        # for (k,v) in inspect.getmembers(r):
        #     print "%20s  %s"%(k,repr(v))
        # print "__dict__:"
        # for k in r.__dict__:
        #     print "[%20s]  %s"%(k,repr(r.__dict__[k]))
