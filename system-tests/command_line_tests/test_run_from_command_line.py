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
                'poi:(1066.13, 444.48) z: None ; (2.13, 3.48) ; 1, OK ; 2.065728692650015',
                'poi:(1208.09, 554.11) z: None ; (44.09, 113.11) ; 1, OK ; 3.7961566857233815',
                'poi:(1190.10, 1412.22) z: None ; (3.10, -1.78) ; 1, OK ; 1.8027515158768608',
            )

