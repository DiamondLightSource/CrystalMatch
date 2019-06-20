import sys

from os.path import realpath, join

from system_test import SystemTest


class TestCommandLineFlags(SystemTest):
    """
    Test the version, json and job_id command line flags
    """
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_version_flag_displays_version_number(self):
        cmd_line = "--version"
        self.run_crystal_matching_test(self.test_version_flag_displays_version_number.__name__, cmd_line)

        # Check for version flag on stdout
        if sys.version_info[0] < 3: # change in ArgumentParser affecting version python3
            self.failUnlessStdErrContainsRegex("[0-9]+[.][0-9]+[.][0-9]+")
        else:
            self.failUnlessStdOutContainsRegex("[0-9]+[.][0-9]+[.][0-9]+")

    def test_json_flag_prints_json_to_console(self):
        cmd_line = "--to_json {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_json_flag_prints_json_to_console.__name__, cmd_line)

        # Check that the output contains JSON instead of human-readable output
        self.failUnlessStdOutContains('"status": {')
        self.failUnlessStdOutContains('"msg": "OK"')
        self.failUnlessStdOutContains('"code": 1')
        self.failIfStdOutContains('align_status:1, OK')

    def test_job_id_flag_displays_job_id_in_output(self):
        cmd_line = "--job test_case {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_job_id_flag_displays_job_id_in_output.__name__, cmd_line)

        # Check for job_id in output
        self.failUnlessStdOutContains('job_id:"test_case"')

    def test_job_id_shortcut_flag_displays_job_id_in_output(self):
        cmd_line = "-j test_case {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_job_id_shortcut_flag_displays_job_id_in_output.__name__, cmd_line)

        # Check for job_id in output
        self.failUnlessStdOutContains('job_id:"test_case"')

    def test_processed_file_is_stored_in_directory_specified_by_output_flag(self):
        cmd_line = "--output pro -j test_case {resources}/stacking/ideal.tif {resources}/stacking/levels"
        self.run_crystal_matching_test(
            self.test_processed_file_is_stored_in_directory_specified_by_output_flag.__name__, cmd_line)
        self.failUnlessDirContainsFile(join(self.get_active_test_dir(), 'pro'), 'processed.tif')

    def test_processed_file_is_stored_in_directory_specified_by_shortcut_output_flag(self):
        cmd_line = "-o pro -j test_case {resources}/stacking/ideal.tif {resources}/stacking/levels"
        self.run_crystal_matching_test(
            self.test_processed_file_is_stored_in_directory_specified_by_shortcut_output_flag.__name__, cmd_line)
        self.failUnlessDirContainsFile(join(self.get_active_test_dir(), 'pro'), 'processed.tif')