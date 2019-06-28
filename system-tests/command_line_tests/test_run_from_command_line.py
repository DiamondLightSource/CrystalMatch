import cv2
from os.path import realpath

from system_test import SystemTest

OPENCV_MAJOR = cv2.__version__[0]
class TestRunFromCommandLine(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_runs_with_image_alignment_only(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_runs_with_image_alignment_only.__name__, cmd_line)

        # Check stdout for correct alignment
        self.failUnlessStdOutContains("align_status:1, OK")

    def test_runs_with_images_and_points(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 1068,442 1168,442 1191,1415"
        self.run_crystal_matching_test(self.test_runs_with_images_and_points.__name__, cmd_line)

        # Check that all three points were transformed
        # results are slightly different for the newer version of opencv
        if int(OPENCV_MAJOR) == 2:
            self.failUnlessStdOutContains(
                'poi:(1065.21, 444.42) z: None ; (0.21, 4.42) ; 1, OK ; 1.9082713294',
                'poi:(1207.72, 552.65) z: None ; (42.72, 112.65) ; 1, OK ; 2.58165335008',
                'poi:(1190.95, 1411.78) z: None ; (2.95, -1.22) ; 1, OK ; 2.06714213361',
            )
        else:
            self.failUnlessStdOutContains(
                'poi:(1065.35, 444.32) z: None ; (1.35, 3.32) ; 1, OK ; 1.9700065120675831',
                'poi:(1208.64, 553.41) z: None ; (44.64, 112.41) ; 1, OK ; 5.326269945675256',
                'poi:(1189.32, 1412.62) z: None ; (2.32, -1.38) ; 1, OK ; 1.9125616895482151',
            )

