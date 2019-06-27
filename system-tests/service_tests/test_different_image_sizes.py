import cv2
from os.path import realpath

from CrystalMatch.dls_util.shape.point import Point
from system_test import SystemTest

OPENCV_MAJOR = cv2.__version__[0]

class TestDifferentImageSizes(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_first_image_smaller_than_second(self):
        cmd_line = "{resources}/A03_crop.jpg {resources}/A03.jpg"
        self.run_crystal_matching_test(self.test_first_image_smaller_than_second.__name__, cmd_line)

        # Check global alignment transform match expected
        scale, x_trans, y_trans = self.get_global_transform_from_std_out()
        self.assertEqual(1, scale)
        self.assertAlmostEqual(223, x_trans, delta=5)
        self.assertAlmostEqual(172, y_trans, delta=5)

    def test_second_image_smaller_than_first(self):
        cmd_line = "{resources}/A02.jpg {resources}/A02_crop.jpg"
        self.run_crystal_matching_test(self.test_second_image_smaller_than_first.__name__, cmd_line)

        # Check global alignment transform match expected
        scale, x_trans, y_trans = self.get_global_transform_from_std_out()
        self.assertEqual(1, scale)
        self.assertAlmostEqual(-155, x_trans, delta=5)
        self.assertAlmostEqual(-70, y_trans, delta=5)

    def test_points_translate_correctly_from_smaller_first_image(self):
        cmd_line = "{resources}/A03_crop.jpg {resources}/A03.jpg 447,1153 408,1069 921,785"
        self.run_crystal_matching_test(self.test_points_translate_correctly_from_smaller_first_image.__name__, cmd_line)

        if int(OPENCV_MAJOR) == 2:
            # Test the POI results
            self.failUnlessPoiAlmostEqual([
                [Point(670, 1325), Point(0, 0), 0, 0.0],
                [Point(631, 1241), Point(0, 0), 1, 0.0],
                [Point(1144, 957), Point(0, 0), 0, 0.0]],
                [5, 5.4, 5]
            )
        else: #new opencv - different values
            self.failUnlessPoiAlmostEqual([
                [Point(670, 1325), Point(0, 0), 1, 0.0],
                [Point(631, 1241), Point(0, 0), 1, 0.0],
                [Point(1144, 957), Point(0, 0), 1, 0.0]],
                [5, 6.6, 5.8]
            )

    def test_points_translate_correctly_to_smaller_second_image(self):
        cmd_line = "{resources}/A02.jpg {resources}/A02_crop.jpg 576,1283 1265,1136 696,630"
        self.run_crystal_matching_test(self.test_points_translate_correctly_to_smaller_second_image.__name__, cmd_line)

        # Test the POI results
        self.failUnlessPoiAlmostEqual([
            [Point(421, 1213), Point(0, 0), 1, 0.0],
            [Point(1110, 1066), Point(0, 0), 0, 0.0],
            [Point(541, 560), Point(0, 0), 0, 0.0]],
            [5.6, 5, 5.6]
        )
