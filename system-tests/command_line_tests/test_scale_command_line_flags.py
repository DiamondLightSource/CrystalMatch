from os.path import realpath

from parameterized import parameterized

from system_test import SystemTest


class TestScaleCommandLineFlags(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_scale_is_read_from_configuration_file_when_flags_not_set(self):
        cmd_line = "{resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = self.test_scale_is_read_from_configuration_file_when_flags_not_set.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.5)

    def test_set_scale_flag_for_input_image_only(self):
        cmd_line = "--scale 1.33333:1 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_set_scale_flag_for_input_image_only.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.333)

    def test_set_scale_flag_for_output_image_only(self):
        cmd_line = "--scale 1.0:0.75 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_set_scale_flag_for_output_image_only.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.333)

    def test_set_scale_flag_for_output_image_only_scaled_by_10(self):
        cmd_line = "--scale 10:7.5 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_set_scale_flag_for_output_image_only_scaled_by_10.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.333)

    def test_set_scale_flags_for_both_images(self):
        cmd_line = "--scale 2:1.333333 {resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = self.test_set_scale_flags_for_both_images.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.5)

    @parameterized.expand(
        [
            ["invalid_val", "--scale not_a_val"],
            ["output_invalid_too_many_values", "--scale 4.5:1:5.4"],
            ["output_invalid_too_few_values", "--scale 4.5:1:5.4"],
        ]
    )
    def test_scale_flags_with_invalid_arg_number_raises_error(self, name, cmd_input):
        cmd_line = cmd_input + " {resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = "test_scale_flags_with_invalid_value_raises_error_" + name
        self.run_crystal_matching_test(test_name, cmd_line)
        self.failUnlessStdErrContains("Scale flag requires two values separated by a colon':'. Value given: ")

    @parameterized.expand(
        [
            ["invalid_val_with_colon", "--scale not_a_val:4.5"],
            ["invalid_on_left", "--scale 0.5.4:1"],
            ["invalid_on_right", "--scale 1:0.5.4"],
        ]
    )
    def test_scale_flags_with_invalid_value_raises_error(self, name, cmd_input):
        cmd_line = cmd_input + " {resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = "test_scale_flags_with_invalid_value_raises_error_" + name
        self.run_crystal_matching_test(test_name, cmd_line)
        self.failUnlessStdErrContains("Scale must be given as a pair of float values separated by a colon (':'). "
                                      "Value given:")

    def test_scale_flag_with_values_causing_incorrect_alignment_returns_failure(self):
        # Run app wit scale deliberately inverted
        cmd_line = "--scale 7.5:10 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_scale_flag_with_values_causing_incorrect_alignment_returns_failure.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        self.failUnlessStdOutContains("align_status:0, FAIL")

    def test_scaling_causing_invalid_overlap_of_matched_areas_returns_failure(self):
        """ Note: This test was added to cover a specific issue which caused a crash using the parameters below. The
        scaling causes an invalid alignment match where the proposed solution does not contain intersecting regions
        of interest causing an None value to be returned. """
        cmd_line = "{resources}/A10_2.jpg {resources}/A10_2@0.5.jpg 756,412 --scale 1:0.5"
        test_name = self.test_scaling_causing_invalid_overlap_of_matched_areas_returns_failure.__name__
        self.run_crystal_matching_test(test_name, cmd_line)
        self.failUnlessStdOutContains("align_status:0, FAIL")

    def failUnlessGlobalAlignmentIsValid(self, expected_scale):
        scale, x_trans, y_trans = self.get_global_transform_from_std_out()
        self.assertAlmostEqual(expected_scale, scale, delta=0.001)
        self.assertAlmostEqual(0, x_trans, delta=1)
        self.assertAlmostEqual(0, y_trans, delta=1)
        self.failUnlessStdOutContains("align_status:1, OK")
