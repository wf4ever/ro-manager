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
from MiscUtils import TestUtils
from ro_utils import parse_job

class TestEvoCommands(TestROEVOSupport.TestROEVOSupport):
    
    TEST_RO_ID = "ro-manger-evo-test-ro"
    TEST_SNAPHOT_ID = "ro-manager-evo-test-snaphot"
    TEST_ARCHIVE_ID = "ro-manager-evo-test-archive-id"
    TEST_UNDEFINED_ID = "ro-manager-evo-test-undefined-id"
    CREATED_RO = ""
    
    def setUp(self):
        super(TestEvoCommands, self).setUp()
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        self.CREATED_RO = rouri;
        return

    def tearDown(self):
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.TEST_SNAPHOT_ID+"/")
        (status, reason) = self.rosrs.deleteRO(self.CREATED_RO)
        super(TestEvoCommands, self).tearDown()
        return
    
    def testSnapshot(self):
        """
        snapshot <live-RO> <snapshot-id> [ --asynchronous ] [ --freeze ] [ -t <access_token> ] [ -t <token> ]
        """
        return
    
    def testSnapshotAsynchronous(self):
        args = [
            "ro", "snapshot" , str(self.CREATED_RO), self.TEST_SNAPHOT_ID, 
            "--asynchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]    
        outLines = ""
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well            
            for word in ("ro snapshot --asynchronous "+ro_test_config.ROSRS_URI + self.TEST_RO_ID + " " + self.TEST_SNAPHOT_ID).split(" "):
                self.assertTrue(self.outstr.getvalue().count(word+ " ") or self.outstr.getvalue().count(" " + word), "snapshot command wasn't parse well")
            self.assertEqual(self.outstr.getvalue().count("Job Status: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Job URI: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Target URI: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Target Name: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Response Status: "), 1)
            self.assertEqual(self.outstr.getvalue().count("Response Reason: "), 1)
            outLines = self.outstr.getvalue().split("\n")
        for line in outLines:
            if "Job URI:" in line:
                jobLocation = line.split("Job URI:")[1].strip()
                status = "RUNNING"
                while status == "RUNNING":
                    (status, id) = parse_job(self.rosrs, jobLocation)
                assert status == "DONE"
                self.rosrs.deleteRO(id)
        return
    
    def testSnapshotSynchronous(self):
        args = [
            "ro", "snapshot", self.CREATED_RO, self.TEST_SNAPHOT_ID, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        outLines = ""
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            for word in ("ro snaphot "+ro_test_config.ROSRS_URI + self.TEST_RO_ID + " " + self.TEST_SNAPHOT_ID).split(" "):
                    self.assertTrue(self.outstr.getvalue().count(word+ " ") or self.outstr.getvalue().count(" " + word), "snapshot command wasn't parse well")
            self.assertEqual(self.outstr.getvalue().count("Target URI: "), 1)
            outLines = self.outstr.getvalue().split("\n")
        for line in outLines:
            if "Target URI:" in line:
                id = line.split("Target URI:")[1].strip()
                self.rosrs.deleteRO(id)
        return
    

    def testSnapshotWithEscOption(self):
        
        args = [
            "ro", "snapshot", self.CREATED_RO,  self.TEST_SNAPHOT_ID, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        outLines = ""
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            self.assertEqual(self.outstr.getvalue().count("--asynchronous"), 0, "shouldn't be asynchronous")
            outLines = self.outstr.getvalue().split("\n")
        for line in outLines:
            if "Target URI:" in line:
                id = line.split("Target URI:")[1].strip()
                self.rosrs.deleteRO(id)
        return
    
    
    def testArchive(self):
        """
        archive <live-RO> <snapshot-id> [ --asynchronous ] [ --freeze ] [ -t <access_token> ] [ -t <token> ]
        """
        return
    
    def testArchiveAsynchronous(self):
        args = [
            "ro", "archive" , str(self.CREATED_RO), self.TEST_SNAPHOT_ID, 
            "--asynchronous",
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]    
        outLines = ""
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
            outLines = self.outstr.getvalue().split("\n")
        for line in outLines:
            if "Job URI:" in line:
                jobLocation = line.split("Job URI:")[1].strip()
                status = "RUNNING"
                while status == "RUNNING":
                    (status, id) = parse_job(self.rosrs, jobLocation)
                assert status == "DONE"
                self.rosrs.deleteRO(id)
        return
    
    
    def testArchiveSynchronous(self):
        args = [
            "ro", "archive", ro_test_config.ROSRS_URI + self.TEST_RO_ID, ro_test_config.ROSRS_URI + self.TEST_SNAPHOT_ID, 
            "-t", ro_test_config.ROSRS_ACCESS_TOKEN,
            "-r", ro_test_config.ROSRS_URI,
            "-v"
        ]
        outLines = ""
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
            # simple check if the verbouse mode works well
            self.assertEqual(self.outstr.getvalue().count("--asynchronous"), 0, "shouldn't be asynchronous")
            outLines = self.outstr.getvalue().split("\n")
        for line in outLines:
            if "Target URI:" in line:
                id = line.split("Target URI:")[1].strip()
                self.rosrs.deleteRO(id)
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
            "ro", "freeze",str(createdSnapshotId), 
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
            "ro", "status", str(createdSnapshotUri),
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
        return

    def testRemoteStatusArchiveRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, createdRoUri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        (status, reason) = self.rosrs.deleteRO(self.TEST_ARCHIVE_ID + "/")
        (createdArchiveStatus, createdArchiveUri) = self.createArchive(createdRoUri, self.TEST_ARCHIVE_ID, True)
        
        args = [
            "ro", "status", str(createdArchiveUri),
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
        return

    def testRemoteStatusUndefinedRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, createdRoUri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        (status, reason) = self.rosrs.deleteRO(self.TEST_ARCHIVE_ID + "/")
        (createdArchiveStatus, createdArchiveUri) = self.createArchive(createdRoUri, self.TEST_ARCHIVE_ID, False)
        
        args = [
            "ro", "status", str(createdArchiveUri),
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
        return

    def testRemoteStatusLiveRO(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        (status, reason) = self.rosrs.deleteRO(self.TEST_RO_ID+"/")
        (status, reason, rouri, manifest) = self.rosrs.createRO(self.TEST_RO_ID,
            "Test RO for ROEVO", "Test Creator", "2012-09-06")
        args = [
            "ro", "status", str(rouri),
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
        return
    
    
    def testRemoteStatusWithWrongUriGiven(self):
        self.rosrs = ROSRS_Session(ro_test_config.ROSRS_URI, accesskey=ro_test_config.ROSRS_ACCESS_TOKEN)
        self.rosrs.deleteRO(self.TEST_RO_ID + "/")
        self.rosrs.deleteRO("some-strange-uri/")
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
            , "testSnapshotWithEscOption"
            , "testArchiveAsynchronous"
            , "testArchiveSynchronous"
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
