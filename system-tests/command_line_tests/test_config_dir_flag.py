from os.path import realpath, join

from system_test import SystemTest


class TestCommandLineConfigFlag(SystemTest):
    expected_config_files = ["align.ini", "crystal.ini", "det_blob.ini", "det_brisk.ini", "det_fast.ini", "det_star.ini", "det_orb.ini", "det_mser.ini"]

    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_config_flag_creates_dir_named_config(self):
        cmd_line = "--config ./test/dir/path {resources}/A01_1.jpg {resources}/A01_2.jpg"
        output_dir = self.run_crystal_matching_test(self.test_config_flag_creates_dir_named_config.__name__, cmd_line)
        self.validate_config_dir(output_dir)

    def test_config_flag_recognises_config_dir(self):
        cmd_line = "--config ./test/dir/path/config {resources}/A01_1.jpg {resources}/A01_2.jpg"
        output_dir = self.run_crystal_matching_test(self.test_config_flag_recognises_config_dir.__name__, cmd_line)

        # Check that the application has not nested an extra 'config' as it is already included in the path
        self.validate_config_dir(output_dir)

    def validate_config_dir(self, output_dir):
        # Check configuration directory exists
        expected_config_dir = join(output_dir, "test", "dir", "path", "config")
        self.failUnlessDirExists(expected_config_dir)
        self.failUnlessDirContainsFiles(expected_config_dir, self.expected_config_files)
        # Test that a warning message is shown when the config dir does not exist
        #self.failUnlessStdErrContains("WARNING", "Configuration directory not found, directory will be created") #goes to loging tests

    def test_config_flag_checks_for_ini_file(self):
        cmd_line = "--config ./renamed_config_dir {resources}/A01_1.jpg {resources}/A01_2.jpg"
        output_dir = self.run_crystal_matching_test(self.test_config_flag_checks_for_ini_file.__name__, cmd_line)

        # Check renamed_config_dir has been used as the config dir
        expected = self.expected_config_files[:]
        expected.append("generic_config_file.ini")
        self.failUnlessDirContainsFiles(join(output_dir, "renamed_config_dir"), expected)
        self.failIfDirExists(join(output_dir, "renamed_config_dir", "config"))
