from os.path import realpath

from parameterized import parameterized

from CrystalMatch.dls_util.shape.point import Point
from system_test import SystemTest


class TestImageScaling(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_smaller_beam_line_image(self, suffix, config_file):
        test_name = "test_alignment_with_smaller_beam_line_image - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_2.jpg {resources}/A10_2@0.5.jpg " \
                                               "--scale 0.5:1"
        self.run_crystal_matching_test(test_name, cmd_line)

        # Check the global transformation, status and error margin
        scale, x, y = self.get_global_transform_from_std_out()
        self.assertEqual(scale, 0.5)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        matches = self.regex_from_std_out('align_error:(.*)')
        self.assertEqual(1, len(matches))
        self.failUnlessStdOutContains('align_status:1, OK')

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_larger_beam_line_image(self, suffix, config_file):
        test_name = "test_alignment_with_larger_beam_line_image - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_2@0.5.jpg {resources}/A10_2.jpg " \
                                               "--scale 1:0.5"
        self.run_crystal_matching_test(test_name, cmd_line)

        # Check the global transformation, status and error margin
        scale, x, y = self.get_global_transform_from_std_out()
        self.assertEqual(scale, 2.0)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        matches = self.regex_from_std_out('align_error:(.*)')
        self.assertEqual(1, len(matches))
        self.failUnlessStdOutContains('align_status:1, OK')

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_smaller_beam_line_image_with_points(self, suffix, config_file):
        test_name = "test_alignment_with_smaller_beam_line_image_with_points - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_2.jpg {resources}/A10_2@0.5.jpg 756,412 " \
                                               "--scale 0.5:1"
        self.run_crystal_matching_test(test_name, cmd_line)

        # Check Points of interest are found and reported at correct co-ordinates
        self.failUnlessPoiAlmostEqual([[Point(378, 206), Point(0, 0), 1, 0]], deltas=(2, 2, 2))

    @parameterized.expand([
        ("average_translation", "{resources}/configs/config_transform_av_translation"),
        ("affine_transform", "{resources}/configs/config_transform_affine_transform"),
        ("homography", "{resources}/configs/config_transform_homography"),
    ])
    def test_alignment_with_larger_beam_line_image_with_points(self, suffix, config_file):
        test_name = "test_alignment_with_larger_beam_line_image_with_points - " + suffix
        cmd_line = "--config " + config_file + " {resources}/A10_2@0.5.jpg {resources}/A10_2.jpg 378,206 " \
                                               "--scale 1:0.5"
        self.run_crystal_matching_test(test_name, cmd_line)

        # Check Points of interest are found and reported at correct co-ordinates
        self.failUnlessPoiAlmostEqual([[Point(756, 413), Point(2, 2), 1, 2.5]], deltas=(2, 2.1, 2))
