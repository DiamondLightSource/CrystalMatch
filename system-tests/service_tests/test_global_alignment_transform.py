from os.path import realpath

from parameterized import parameterized

from CrystalMatch.dls_util.shape.point import Point
from system_test import SystemTest


class TestGlobalAlignmentTransform(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_on_identical_image(self, suffix, config_file):
        test_name = "test_alignment_on_identical_image - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_1.jpg {resources}/A10_1.jpg 871,590"
        self.run_crystal_matching_test(test_name, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.assertEqual(1.0, scale)
        self.assertEqual(0, x_trans)
        self.assertEqual(0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(871, 590), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_positive_offset_on_image_b(self, suffix, config_file):
        test_name = "test_alignment_with_positive_offset_on_image_b - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_1@-10-10.jpg {resources}/A10_1.jpg 871,590"
        self.run_crystal_matching_test(test_name, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.assertEqual(1.0, scale)
        self.assertEqual(10.0, x_trans)
        self.assertEqual(10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(881, 600), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_negative_offset_on_image_b(self, suffix, config_file):
        test_name = "test_alignment_with_negative_offset_on_image_b - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_1.jpg {resources}/A10_1@-10-10.jpg 871,590"
        self.run_crystal_matching_test(test_name, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.assertEqual(1.0, scale)
        self.assertEqual(-10.0, x_trans)
        self.assertEqual(-10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(861, 580), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_mixed_offset_on_image_b(self, suffix, config_file):
        test_name = "test_alignment_with_mixed_offset_on_image_b - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_1@-10-0.jpg {resources}/A10_1@-0-10.jpg 871,590"
        self.run_crystal_matching_test(test_name, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.assertEqual(1.0, scale)
        self.assertEqual(10.0, x_trans)
        self.assertEqual(-10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(881, 580), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_mixed_offset_counterpoint_on_image_b(self, suffix, config_file):
        test_name = "test_alignment_with_mixed_offset_counterpoint_on_image_b - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_1@-0-10.jpg {resources}/A10_1@-10-0.jpg 871,590"
        self.run_crystal_matching_test(test_name, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.assertEqual(1.0, scale)
        self.assertEqual(-10.0, x_trans)
        self.assertEqual(10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(861, 600), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)
