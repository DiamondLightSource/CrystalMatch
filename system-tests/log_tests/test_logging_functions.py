from os.path import realpath, join

from system_test import SystemTest


class TestLoggingFunctions(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_log_file_is_created(self):
        cmd_line = "--log logs {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_file_is_created.__name__, cmd_line)

        log_dir =  join(self.get_active_test_dir(), "logs")
        # Check default log directory exists.
        self.failUnlessDirContainsFile(log_dir, "log")

    def test_logging_flag_overrides_default_log_dirs(self):
        cmd_line = "--log test/logging/flag/ {resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_logging_flag_overrides_default_log_dirs.__name__, cmd_line)

        # Check specified log dir exists
        self.failIfDirExists(join(self.get_active_test_dir(), "logs"))
        log_dir = join(self.get_active_test_dir(), "test", "logging", "flag")
        #log_image_dir = join(log_dir, "images")
        # logs are now only kept next to the image debug.log is not created anymore
        self.failUnlessDirContainsFile(log_dir, "log")
        #self._verify_logged_image_files(log_image_dir, self.get_poi_from_std_out())

    def test_log_file_contains_job_id_if_set(self):
        cmd_line = "--log logs -j test_job_123 {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_file_contains_job_id_if_set.__name__, cmd_line)

        # Verify that the log file contains the job ID
        self.failUnlessFileContains(join(self._active_log_dir(), "log"),
                                    "'job_id': 'test_job_123'")

    def test_logging_flag_with_invalid_path_reports_error(self):
        cmd_line = "--log test/log:ging/flag/ {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_logging_flag_with_invalid_path_reports_error.__name__, cmd_line)

        # Check std_err for error message return value for failure
        try:
            self.failUnlessStdErrContains(
                "ERROR:root:Could not create find/create directory, path may be invalid: test/log:ging/flag/")
            self.failUnlessRunFailed()
        except AssertionError:
            # Note - this error is only really possible in Windows, if the file has been created successfully then
            # this is probably a Linux system and the test should pass.
            self.failUnlessDirContainsFile(join(self.get_active_test_dir(), "test", "log:ging", "flag"), "log")

    def test_processed_file_is_stored_in_log_when_running_with_stucking(self):
        cmd_line = "--log logs -j test_case {resources}/stacking/ideal.tif {resources}/stacking/levels"
        self.run_crystal_matching_test(self.test_processed_file_is_stored_in_log_when_running_with_stucking.__name__, cmd_line)
        dir = self._active_log_dir()
        self.failUnlessDirContainsFile(dir,'processed.tif')

    def _active_log_dir(self):
        return join(self.get_active_test_dir(), "logs")