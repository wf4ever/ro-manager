import sys 

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

#internal
import rocommand.ro as ro
from urlparse import urljoin
import TestROEVOSupport
from ROSRS_Session import ROSRS_Session
from TestConfig import ro_test_config
from StdoutContext import SwitchStdout
#external
from MiscLib import TestUtils

class TestEvoCommands(TestROEVOSupport.TestROEVOSupport):
    
    TEST_RO_ID = "ro-manger-evo-test-ro"
    TEST_SNAPHOT_ID = "ro-manager-evo-test-snaphot"
    TEST_ARCHIVE_ID = "ro-manager-evo-test-archive-id"
    TEST_UNDEFINED_ID = "ro-manager-evo-test-undefined-id"
    
    
    def setUp(self):
        super(TestEvoCommands, self).setUp()
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        return

    def tearDown(self):
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
        super(TestEvoCommands, self).tearDown()
        return
    
    def testSnapshot(self):
        """
        snapshot <live-RO> <snapshot-id> [ --synchronous | --asynchronous ] [ --freeze ] [ -t <access_token> ] [ -t <token> ]
        """
        return
    
    def testSnapshotAsynchronous(self):
        args = [
            "ro", "snapshot" , ro_test_config.ROSRS_URI + self.TEST_RO_ID, self.TEST_SNAPHOT_ID, 
            "--asynchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]    
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            for word in ("ro snaphot --asynchronous "+ro_test_config.ROSRS_URI + self.TEST_RO_ID + " " + self.TEST_SNAPHOT_ID).split(" "):
                self.assertTrue(self.outstr.getvalue().count(word+ " ") or self.outstr.getvalue().count(" " + word), "snapshot command wasn't parse well")
            self.assertEqual(self.outstr.getvalue().count("Job Status: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Job URI: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Target URI: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Target Name: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Response Status: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Response Reason: "), 1)
        return
    
    def testSnapshotSynchronous(self):
        args = [
            "ro", "snapshot", ro_test_config.ROSRS_URI + self.TEST_RO_ID, ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID, 
            "--synchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            for word in ("ro snaphot --synchronous "+ro_test_config.ROSRS_URI + self.TEST_RO_ID + " " + self.TEST_SNAPHOT_ID).split(" "):
                    self.assertTrue(self.outstr.getvalue().count(word+ " ") or self.outstr.getvalue().count(" " + word), "snapshot command wasn't parse well")
            self.assertEqual(self.outstr.getvalue().count("Target URI: "), 1)
            self.assertGreaterEqual(self.outstr.getvalue().count("Target Name: "), 1)
            self.assertGreaterEqual(self.outstr.getvalue().count("Job Status: "), 1)
        return
    
    def testSnapshotAmbiguous(self):
        args = [
            "ro", "snapshot", ro_test_config.ROSRS_URI + self.TEST_RO_ID, ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID, 
            "--asynchronous",
            "--synchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 1
            # simple check if the verbouse mode works well
            self.assertEqual(self.outstr.getvalue().count("ambiguous call --synchronous and --asynchronous, choose one"),1 , "snapshot command should be reported as ambiguous")
        return
    
    
    def testSnapshotWithEscOption(self):
        
        args = [
            "ro", "snapshot", ro_test_config.ROSRS_URI + self.TEST_RO_ID + "/", self.TEST_SNAPHOT_ID, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            self.assertEqual(self.outstr.getvalue().count("--synchronous"), 0, "shouldn't be synchronous")
            self.assertEqual(self.outstr.getvalue().count("--asynchronous"), 0, "shouldn't be asynchronous")
            self.assertEqual(self.outstr.getvalue().count("--asynchronous"), 0, "[ESC]")
        return
    
    
    def testArchive(self):
        """
        archive <live-RO> <snapshot-id> [ --synchronous | --asynchronous ] [ --freeze ] [ -t <access_token> ] [ -t <token> ]
        """
        return
    
    def testArchiveAsynchronous(self):
        args = [
            "ro", "archive" , ro_test_config.ROSRS_URI + self.TEST_RO_ID, self.TEST_SNAPHOT_ID, 
            "--asynchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]    
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            for word in ("ro archive --asynchronous "+ro_test_config.ROSRS_URI + self.TEST_RO_ID + " " + self.TEST_SNAPHOT_ID).split(" "):
                self.assertTrue(self.outstr.getvalue().count(word+ " ") or self.outstr.getvalue().count(" " + word), "snapshot command wasn't parse well")
            self.assertEqual(self.outstr.getvalue().count("Job Status: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Job URI: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Target URI: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Target Name: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Response Status: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Response Reason: "), 1)
        return
    
    def testArchiveSynchronous(self):
        args = [
            "ro", "archive", ro_test_config.ROSRS_URI + self.TEST_RO_ID, ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID, 
            "--synchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            for word in ("ro archive --synchronous "+ro_test_config.ROSRS_URI + self.TEST_RO_ID + " " + self.TEST_SNAPHOT_ID).split(" "):
                    self.assertTrue(self.outstr.getvalue().count(word+ " ") or self.outstr.getvalue().count(" " + word), "snapshot command wasn't parse well")
            self.assertEqual(self.outstr.getvalue().count("Target URI: "), 1)
            self.assertGreaterEqual(self.outstr.getvalue().count("Target Name: "), 1)
            self.assertGreaterEqual(self.outstr.getvalue().count("Job Status: "), 1)
        return
    
    def testArchiveAmbiguous(self):
        args = [
            "ro", "archive", ro_test_config.ROSRS_URI + self.TEST_RO_ID, ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID, 
            "--asynchronous",
            "--synchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 1
            self.assertEqual(self.outstr.getvalue().count("ambiguous call --synchronous and --asynchronous, choose one"),1 , "archive command should be reported as ambiguous")
        return
    
    
    def testArchiveWithEscOption(self):
        args = [
            "ro", "archive", ro_test_config.ROSRS_URI + self.TEST_RO_ID, ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            self.assertEqual(self.outstr.getvalue().count("--synchronous"), 0, "shouldn't be synchronous")
            self.assertEqual(self.outstr.getvalue().count("--asynchronous"), 0, "shouldn't be asynchronous")
            self.assertEqual(self.outstr.getvalue().count("--asynchronous"), 0, "[ESC]")
        return
    
    def testFreeze(self):
        """
        freeze <RO-id> 
        """
        #preapre snaphot
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")

        (status, reason, createdRoUri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")        
        (createdSnapshotStatus, createdSnapshotId) =  self.createSnapshot(createdRoUri, self.TEST_SNAPHOT_ID, False)
        args = [
            "ro", "freeze",createdSnapshotId , 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            self.assertEqual(self.outstr.getvalue().count("freeze operation finished successfully"), 1)
        (status, reason) = self.rosrs.deleteRO(createdRoUri)
        (status, reason) = self.rosrs.deleteRO(createdSnapshotId)
        return
        
    def FreezeNonExistetSnaphot(self):
        """
        freeze <RO-id> 
        """
        #preapre snaphot
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")

        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")        
        self.createSnapshot(self.TEST_RO_ID+"/", self.TEST_SNAPHOT_ID, True)
        
        args = [
            "ro", "freeze", self.TEST_SNAPHOT_RO_ID + "non exited", 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == -1
            self.assertEqual(self.outstr.getvalue().count("Given URI isn't correct"), 0)
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        return
    
    def testRemoteStatusSnapshotRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, createdRoUri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID + "/")
        (createdSnapshotStatus, createdSnapshotUri) = self.createSnapshot(createdRoUri, self.TEST_SNAPHOT_ID, True)
        
        args = [
            "ro", "status", createdSnapshotUri,
            "-r", ro_test_config.ROSRS_URI, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            outtxt = self.outstr.getvalue()
            self.assertEqual(outtxt.count("SNAPSHOT"), 1)
        (status, reason) = self.rosrs.deleteRO(createdSnapshotUri)
        (status, reason) = self.rosrs.deleteRO(createdRoUri)
        
    def testRemoteStatusArchiveRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, createdRoUri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        (status, reason) = self.rosrs.deleteRO(self.TEST_ARCHIVE_ID + "/")
        (createdArchiveStatus, createdArchiveUri) = self.createArchive(createdRoUri, self.TEST_ARCHIVE_ID, True)
        
        args = [
            "ro", "status", createdArchiveUri,
            "-r", ro_test_config.ROSRS_URI,
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            outtxt = self.outstr.getvalue()
            self.assertEqual(outtxt.count("ARCHIVE"), 1)
        (status, reason) = self.rosrs.deleteRO(createdArchiveUri)
        (status, reason) = self.rosrs.deleteRO(createdRoUri)
    
    def testRemoteStatusUndefinedRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, createdRoUri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        (status, reason) = self.rosrs.deleteRO(self.TEST_ARCHIVE_ID + "/")
        (createdArchiveStatus, createdArchiveUri) = self.createArchive(createdRoUri, self.TEST_ARCHIVE_ID, False)
        
        args = [
            "ro", "status", createdArchiveUri,
            "-r", ro_test_config.ROSRS_URI, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            outtxt = self.outstr.getvalue()
            self.assertEqual(outtxt.count("UNDEFINED"), 1)
        (status, reason) = self.rosrs.deleteRO(createdArchiveUri)
        (status, reason) = self.rosrs.deleteRO(createdRoUri)
    
    def testRemoteStatusLiveRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        
        args = [
            "ro", "status", rouri,
            "-r", ro_test_config.ROSRS_URI, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            outtxt = self.outstr.getvalue()
            self.assertEqual(outtxt.count("LIVE"), 1)
        (status, reason) = self.rosrs.deleteRO(rouri)
    
    
    
    def testRemoteStatusWithWrongUriGiven(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        self.rosrs.deleteRO(self.TEST_RO_ID + "/")
        self.rosrs.deleteRO("some-strange-uri/")
        self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
    
        args = [
            "ro", "status", ro_test_config.ROSRS_URI + "some-strange-uri/",
            "-r", ro_test_config.ROSRS_URI, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-v"
        ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            outtxt = self.outstr.getvalue()
            assert status == -1
            self.assertEqual(outtxt.count("Wrong URI was given"), 1)
        self.rosrs.deleteRO(self.TEST_RO_ID + "/")
        return
    
def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit":
            [ 
            ],
        "component":
            [ "testSnapshotAsynchronous"
            , "testSnapshotSynchronous"
            , "testSnapshotAmbiguous"
            , "testSnapshotWithEscOption"
            , "testArchiveAsynchronous"
            , "testArchiveSynchronous"
            , "testArchiveAmbiguous"
            , "testArchiveWithEscOption"
            , "testFreeze"
            , "testRemoteStatusSnapshotRO"
            , "testRemoteStatusArchiveRO"
            , "testRemoteStatusUndefinedRO"
            , "testRemoteStatusLiveRO"
            , "testRemoteStatusWithWrongUriGiven"
            ],
        "integration":
            [ 
            ],
        "pending":
            [ 
            ]
        }
    return TestUtils.getTestSuite(TestEvoCommands, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestEvoCommands.log", getTestSuite, sys.argv)
