from pkg_resources import require
require("numpy>=1.11.1")

from os.path import realpath, abspath

from CrystalMatch.dls_imagematch.service.service_result import ServiceResult
from system_test import SystemTest


class TestServiceOutput(SystemTest):
    """
    Tests the format of the console output and checks that the results being produced are in the correct co-ordinate
    space.

    NOTE: This Test Case does not test accuracy - these tests should not break due to changes in the algorithm.
    """

    POI_LINE_REGEX_OK = 'poi:\(-?[0-9]+\.[0-9]{2}, -?[0-9]+\.[0-9]{2}\) z: None ; \(-?[0-9]+\.[0-9]{2}, ' \
                        '-?[0-9]+\.[0-9]{2}\) ; 1, OK ; [0-9]+\.[0-9]+\n'
    POI_LINE_REGEX_FAIL = 'poi:\(-?[0-9]+\.[0-9]{2}, -?[0-9]+\.[0-9]{2}\) z: None ; \(-?[0-9]+\.[0-9]{2},' \
                          ' -?[0-9]+\.[0-9]{2}\) ; 0, FAIL ; 0\n'
    ALIGN_TRANSFORM_REGEX = "align_transform:[0-9]+.[0-9]+, \(-?[0-9]+\.[0-9]+, -?[0-9]+\.[0-9]+\)"

    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_output_format_for_valid_run(self):
        cmd_line = "-j 01234 {resources}/A10_1.jpg {resources}/A10_2.jpg 902,435 963,1310"
        self.run_crystal_matching_test(self.test_output_format_for_valid_run.__name__, cmd_line)

        # Test format of alignment output
        self.failUnlessStdOutContains(
            'exit_code:0',
            'job_id:"01234"',
            'input_image:"' + abspath(self.substitute_tokens("{resources}/A10_1.jpg")) + '"',
            'output_image:"' + abspath(self.substitute_tokens("{resources}/A10_2.jpg")) + '"',
        )
        self.failUnlessStdOutContainsRegex(
            'align_status:1, OK\n',
            'align_error:[0-9][0-9]?\.[0-9]+\n',
        )

        # Test format of POI output
        self.failUnlessStdOutContains(ServiceResult.POI_RESULTS_HEADER)
        self.failUnlessStdOutContainsRegexString(
            self.POI_LINE_REGEX_OK,
            count=2
        )

    def test_output_for_failed_image_alignment_without_points(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A10_2.jpg"
        self.run_crystal_matching_test(self.test_output_for_failed_image_alignment_without_points.__name__, cmd_line)

        # Check for fail status in global alignment
        self.failUnlessStdOutContains("align_status:0, FAIL")
        self.failIfStdOutContains(ServiceResult.POI_RESULTS_HEADER)
        self.failIfStdOutContains("poi:")

    def test_output_for_failed_image_alignment_with_points(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A10_2.jpg 902,435 963,1310"
        self.run_crystal_matching_test(self.test_output_for_failed_image_alignment_with_points.__name__, cmd_line)

        # Check for fail status in global alignment
        self.failUnlessStdOutContains("align_status:0, FAIL")
        self.failIfStdOutContains(ServiceResult.POI_RESULTS_HEADER)
        self.failIfStdOutContains("poi:")

    def test_format_for_failed_points(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2.jpg 11,11"
        self.run_crystal_matching_test(self.test_format_for_failed_points.__name__, cmd_line)

        # Check for failed POI result
        self.failUnlessStdOutContains(ServiceResult.POI_RESULTS_HEADER)
        self.failUnlessStdOutContainsRegexString(self.POI_LINE_REGEX_FAIL, count=1)

    def test_format_of_global_transform_with_scaled_image(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2@0.5.jpg 473,921"
        self.run_crystal_matching_test(self.test_format_of_global_transform_with_scaled_image.__name__, cmd_line)

        # Regex test the format of the global transform
        self.failUnlessStdOutContainsRegex(self.ALIGN_TRANSFORM_REGEX)
