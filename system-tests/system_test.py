import json
import re

from os import makedirs, listdir
from os.path import exists, join, splitext, isdir, realpath, split, isfile
from re import match, compile
from shutil import rmtree, copytree
from subprocess import call
from unittest import TestCase

from CrystalMatch.dls_util.shape.point import Point


class SystemTest(TestCase):
    """
    Parent class which provides a framework to run System Tests using the standard Python unittest libraries.
    A system test case should extend this class and include the boilerplate code below to run the
    Crystal Matching algorithm.

    def setUp(self):
        self._set_directory_paths(realpath(__file__))

    def test_something(self):
        # Command line arguments below can be modified for each test.
        self._run_crystal_matching_test("test_something",
                                        "../../input/A01_1.jpg ../../input/A01_2.jpg 1068,442 1191,1415")
        ...

    A Test suite directory is created for each TestCase object based on the file name; this is a convenient place to
    store input files.  Within this directory a global output directory is created which is ignored by git - in turn
    this will contain an output directory for each named test.
    """

    OUTPUT_DIR_NAME = "sys_test_output"
    RESOURCE_DIR_NAME = "resources"
    CONFIG_FLAG = "--config"

    _active_output_dir = None  # Used to store the current active output out dir - should be set when sys test runs.

    def _get_output_dir(self):
        """
        Assert-safe method of retrieving the output directory.
        :return: Output directory for the current test suite
        """
        assert hasattr(self, "_output_dir"), "Output directory not set"
        assert self._output_dir is not None, "Output directory not set correctly!"
        return self._output_dir

    def _get_test_suite_dir(self):
        """
        Assert-safe method of retrieving the test suite directory.
        :return:
        """
        assert hasattr(self, "_test_suite_dir"), "Test directory not set"
        assert self._test_suite_dir is not None, "Test directory not set correctly!"
        return self._test_suite_dir

    def get_active_test_dir(self):
        assert hasattr(self, "_active_output_dir"), "Test directory not set"
        assert self._active_output_dir is not None, "Test directory not set correctly!"
        return self._active_output_dir

    def _input_dir(self):
        return join(self._get_test_suite_dir(), "input")

    def _expected_test_dir(self):
        return join(self._get_test_suite_dir(), "expected", self._current_test_name)

    def set_directory_paths(self, test_file_path):
        """
        Must be included in the setUp() method of the child TestCase.
        :param test_file_path: Must be the result of os.path.realpath(__file__) from the child file.
        """
        # Set test directory
        self._test_suite_dir, extension = splitext(test_file_path)

        # Set output directory
        self._output_dir = join(self._get_test_suite_dir(), self.OUTPUT_DIR_NAME)

    def run_crystal_matching_test(self, test_name, cmd_line_args):
        """
        Run the Crystal Matching algorithm in a sub-process relative to a directory named
        test_name in the Test Suite Output Directory. If the directory already exists it will be overwritten.
        If the --config flag is not included in the command line args it will be set to the output directory.

        The Test Suite Output Directory may contain a directory called 'input' which can be used to store common files
        used by tests.  In addition, if a directory exists with the same name as the test being run the contents of that
        directory will be copied to the directory before the test begins.

        See self.substitute_tokens() for list of available tokens to use in command line.

        :param test_name: Directory name used to store output in the test suite output dir.
        :param cmd_line_args: Command line arguments to be used for the sub-process call.
        :return: The path of the output directory.
        """

        # Set up the output directory - copy input resources
        self._current_test_name = test_name
        self._active_output_dir = join(self._get_output_dir(), test_name)
        if exists(self._active_output_dir):
            rmtree(self._active_output_dir)
        test_input_dir = join(self._input_dir(), test_name)
        if self._is_dir(test_input_dir):
            copytree(test_input_dir, self._active_output_dir)
        else:
            makedirs(self._active_output_dir)

        # Replace tokens in the command line
        cmd_line_args = self.substitute_tokens(cmd_line_args)

        # Set a location for the config if unspecified
        if self.CONFIG_FLAG not in cmd_line_args:
            cmd_line_args = cmd_line_args + " " + self.CONFIG_FLAG + " " + self._active_output_dir

        # Run Crystal Matching Algorithm with command line arguments
        command = "python -m CrystalMatch.dls_imagematch.main_service " + cmd_line_args
        with open(self._get_cmd_line_file_path(), "w") as cmd_out_file:
            cmd_out_file.writelines(command)
        stdout_file = open(self._get_std_out_file_path(), "w")
        stderr_file = open(self._get_std_err_file_path(), "w")
        self._ret_code = call(command, shell=True, cwd=self._active_output_dir, stdout=stdout_file, stderr=stderr_file)
        stdout_file.close()
        stderr_file.close()
        return self._active_output_dir

    def substitute_tokens(self, sub_string):
        """
        Makes the following string substitutions:

         {input} -> replaced with an absolute path to a directory in the test_suite_dir named 'input'.
           usage: {input}/[file]
         {resources} -> replace with an absolute path to a resources directory in the system tests root dir.
           usage: {resources}/[file]
         {expected} - > replaced with an absolute path to a directory with the test name in the 'expected' directory.
        """
        sub_string = sub_string.replace("{input}", self._input_dir())
        sub_string = sub_string.replace("{resources}", self._get_resources_dir())
        sub_string = sub_string.replace("{expected}", self._expected_test_dir())
        return sub_string

    def _get_resources_dir(self):
        """
        Get the path of a resource directory which in the same directory as this file (hackity, hack, hack, hack).
        Saves space in the repository as we can reuse files between tests.
        :return: The path of the System Tests Resources directory.
        """
        sys_test_root, this_file = split(realpath(__file__))
        sys_test_root = join(sys_test_root, self.RESOURCE_DIR_NAME)
        return sys_test_root

    def _get_cmd_line_file_path(self):
        """
        Gets a file path for the cmd_line file used to store the command being run.
        :return: File object for cmd_line file
        """
        return join(self._active_output_dir, "cmd_line")

    def _get_std_out_file_path(self):
        """
        Gets the stdout file path from the current active output directory
        :return: File object for stdout file
        """
        return join(self._active_output_dir, "stdout")

    def _get_std_out(self):
        return self._get_file_contents(self._get_std_out_file_path())

    def _get_std_err(self):
        return self._get_file_contents(self._get_std_err_file_path())

    @staticmethod
    def _get_file_contents(file_path):
        with open(file_path, "r") as f:
            contents = f.read()
        return contents

    @staticmethod
    def floatify_regex_match(matches):
        float_array = []
        for i in range(len(matches)):
            float_array.append([])
            for j in range(len(matches[i])):
                float_array[i].append(float(matches[i][j]))
        return float_array

    @staticmethod
    def _is_dir(directory_path):
        return exists(directory_path) and isdir(directory_path)

    def _get_std_err_file_path(self):
        """
        Gets the stderr file path from the current active output directory
        :return: File object for stderr file
        """
        return join(self._active_output_dir, "stderr")

    # Test Utility Methods
    def failIfRunFailed(self):
        self.assertEqual(0, self._ret_code)

    def failUnlessRunFailed(self):
        self.assertEqual(1, self._ret_code)

    def failUnlessStdOutContains(self, *strings):
        """
        Fail the current test case unless stdout contains these strings.
        :param strings: Strings to match in stdout - can be an array of string or a single string
        """
        self.failUnlessFileContains(self._get_std_out_file_path(), *strings)

    def failIfStdOutContains(self, *strings):
        """
        Fail the current test case if stdout contains any of these strings.
        :param strings: Strings to match in stdout - can be an array of string or a single string
        """
        self.failIfFileContains(self._get_std_out_file_path(), *strings)

    def failIfFileContains(self, file_path, *strings):
        contents = self._get_file_contents(file_path)
        for match_line in strings:
            self.assertFalse(match_line in contents,
                        "Found in file (" + file_path + ") when not expected: " + match_line)

    def failUnlessFileContains(self, file_path, *strings):
        contents = self._get_file_contents(file_path)
        for match_line in strings:
            self.assertTrue(match_line in contents,
                            "Not found in file (" + file_path + ") when expected: " + match_line)

    def failUnlessStdOutContainsRegexString(self, regex, count=0):
        """
        Match a regex string to the contents of StdOut.  Optionally specify the number of matches the output must
        contain.
        :param count: Number of matches required, 0 disables feature and fails if the match does not appear.
        :param regex: Regex to match.
        :return:
        """
        std_out = self._get_std_out()
        compiled_regex = compile(regex)
        if count == 0:
            self.assertTrue(compiled_regex.search(std_out) is not None)
        else:
            matches = compiled_regex.findall(std_out)
            self.assertTrue(matches is not None and len(matches) == count,
                            "Regex expected in output " + str(count) + " time(s): " + regex)

    def failUnlessStdOutContainsRegex(self, *regex):
        for r in regex:
            self.failUnlessStdOutContainsRegexString(r, count=0)

    def failUnlessStdErrContains(self, *strings):
        self.failUnlessFileContains(self._get_std_err_file_path(), *strings)

    def failUnlessStdErrContainsRegex(self, *regex):
        std_err = self._get_std_err()
        for match_line in regex:
            compiled_regex = compile(match_line)
            self.assertTrue(compiled_regex.search(std_err) is not None)

    def failIfStrErrHasContent(self):
        std_err = self._get_std_err()
        self.assertFalse(len(std_err) > 0, "Standard err file shows errors: " + self._get_std_err_file_path())

    def failUnlessDirExists(self, directory_path):
        self.assertTrue(exists(directory_path), "Directory does not exist: " + directory_path)
        self.assertTrue(isdir(directory_path), "Not a directory: " + directory_path)

    def failUnlessDirContainsFileRegex(self, directory_path, regex_filename):
        for file_name in listdir(directory_path):
            if match(regex_filename, file_name):
                return
            self.fail("Could not find regex \"" + regex_filename + "\" in directory: " + directory_path)

    def failUnlessDirContainsFile(self, directory_path, file_name):
        self.assertTrue(self._is_dir(directory_path), "Directory does not exist: " + directory_path)
        self.assertTrue(file_name in listdir(directory_path), "Could not find file \"" + file_name +
                        "\" in directory: " + directory_path)

    def failUnlessDirContainsFiles(self, directory_path, files):
        self.assertTrue(self._is_dir(directory_path), "Directory does not exist: " + directory_path)
        for file_name in files:
            self.failUnlessDirContainsFile(directory_path, file_name)

    def failIfDirExists(self, dir_path):
        self.assertFalse(self._is_dir(dir_path))

    def failUnlessPoiAlmostEqual(self, expected_array, deltas=(0.5, 0.5, 2.0)): # I've increased the deltas slightly
        """
        Extracts POI information from the console output and checks it against the array values using
        assertAlmostEqual - default delta values are set.
        NOTE: This will fail if verbose or debug mode is active
        :param expected_array: An array of POI value arrays which match the format [location, transform, success, error]
        :param deltas: Set the delta values used for checks: ([location, offset, error])
        """
        poi_array = self.get_poi_from_std_out()
        self.assertEqual(len(expected_array), len(poi_array),
                             "Unexpected number of POI. "
                             "Expected: " + str(len(expected_array)) + " Actual: " + str(len(poi_array)))
        for i in range(len(poi_array)):
            loc, off, success, err = poi_array[i]
            self.assertAlmostEqual(expected_array[i][0].x, loc.x, delta=deltas[0])
            self.assertAlmostEqual(expected_array[i][0].y, loc.y, delta=deltas[0])
            self.assertAlmostEqual(expected_array[i][1].x, off.x, delta=deltas[1])
            self.assertAlmostEqual(expected_array[i][1].y, off.y, delta=deltas[1])
            self.assertEqual(expected_array[i][2], success, msg="POI result expected " + str(expected_array[i][2])
                                                                    + " but result was " + str(success))
            self.assertAlmostEqual(expected_array[i][3], err, msg="Error value mismatch", delta=deltas[2])

    def get_global_transform_from_std_out(self):
        """
        Extract the global transform data from the std_out
        :return: Scale, x translation and y translation
        """
        std_out = self._get_std_out()
        re_compile = re.compile("align_transform:([0-9]+\.[0-9]+), \((-?[0-9]+\.[0-9]+), (-?[0-9]+\.[0-9]+)\)")
        matches = re_compile.findall(std_out)
        self.assertEqual(1, len(matches), "Unexpected no. of matches for alignment_transform: " + str(len(matches)))
        float_array = self.floatify_regex_match(matches)
        scale, x_trans, y_trans = float_array[0]
        return scale, x_trans, y_trans

    def regex_from_std_out(self, regex):
        """
        Search std_out and return an array of single values from std_out
        :param regex: Regex expression containing brackets
        :return: An array of matches
        """
        re_compile = re.compile(regex)
        matches = re_compile.findall(self._get_std_out())
        self.assertFalse(matches is None)
        return matches

    def get_poi_from_std_out(self):
        """
        Extract the output POI from the std_out file. - Note this will provide double entries with Verbose mode on.
        :return: Array of POI in the format [location, offset, success, error].
        """
        std_out = self._get_std_out()
        # Match POI lines in the output
        re_compile = re.compile("poi:\((-?[0-9.]+), (-?[0-9.]+)\) z: None ; \((-?[0-9.]+), "
                                "(-?[0-9.]+)\) ; ([012]).* ; ([0-9.]+)")
        matches = re_compile.findall(std_out)
        float_array = self.floatify_regex_match(matches)
        poi_array = []
        for f in float_array:
            # Extract pixel location, offset, success value and mean error
            poi_array.append([Point(f[0], f[1]), Point(f[2], f[3]), f[4], f[5]])
        return poi_array

    def read_json_object_from_std_out(self):
        """
        Assumes that the stdout is a single JSON object and attempts to interpret it - will not work if verbose or debug
         mode are active.
        :return: object represented by JSON.
        """
        return json.loads(self._get_std_out())

    def failUnlessFilesMatch(self, expected_file, actual_file):
        """
        Fail unless the give files exist, are files and their content matches.  Only works on text files and excess
        whitespace at the beginning or end of a line will not cause a failure.
        :param expected_file: Expected file reference.
        :param actual_file: Actual file reference.
        """
        self.assertTrue(exists(expected_file) and isfile(expected_file), "Expected file not found.")
        self.assertTrue(exists(actual_file) and isfile(actual_file), "Actual file not found.")
        with open(expected_file, 'r') as file_r:
            expected_contents = file_r.readlines()
        with open(actual_file, 'r') as file_r:
            actual_contents = file_r.readlines()
        self.assertEqual(len(expected_contents), len(actual_contents), "File length does not match")
        for i in range(len(expected_contents)):
            self.assertEqual(
                expected_contents[i].strip(),
                actual_contents[i].strip(),
                'File Match: Mismatch on line {}: \n"{}"\nvs\n"{}"'.format(str(i),
                                                                           expected_contents[i],
                                                                           actual_contents[i]))
