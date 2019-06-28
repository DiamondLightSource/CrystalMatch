from os.path import realpath, join

from CrystalMatch.dls_util.shape.point import Point
from system_test import SystemTest


class TestCrystalStageConfigFile(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_crystal_config_file_default_match_expected(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2.jpg"
        test_name = self.test_crystal_config_file_default_match_expected.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        test_settings_file = join(self.get_active_test_dir(), 'config', 'crystal.ini')
        expected_settings_file = join(self.substitute_tokens("{expected}"), "crystal.ini")
        self.failUnlessFilesMatch(expected_settings_file, test_settings_file)

    def test_crystal_stage_disabled_by_changing_perform_poi_analysis_option(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_1@-10-10.jpg 123,123 456,456 " \
                   "--config {resources}/configs/config_disable_poi_stage"
        test_name = self.test_crystal_stage_disabled_by_changing_perform_poi_analysis_option.__name__
        self.run_crystal_matching_test(test_name, cmd_line)
        self.failUnlessPoiAlmostEqual([[Point(113, 113), Point(0, 0), 2, 0],
                                       [Point(446, 446), Point(0, 0), 2, 0]],
                                      [0.5, 0, 0])
        self.failUnlessStdOutContains("2, DISABLED")

    def test_crystal_stage_disabled_is_reported_correctly_in_json(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_1@-10-10.jpg 123,456 456,123 " \
                   "--config {resources}/configs/config_disable_poi_stage --to_json"
        test_name = self.test_crystal_stage_disabled_is_reported_correctly_in_json.__name__
        self.run_crystal_matching_test(test_name, cmd_line)
        json = self.read_json_object_from_std_out()

        # Check POI values in json array
        self.assertEqual(2, json['poi'][0]['status']['code'])
        self.assertEqual("DISABLED", json['poi'][0]['status']['msg'])
        self.assertEqual(0, json['poi'][0]['mean_error'])
        self.assertEqual(113, json['poi'][0]['location']['x'])
        self.assertEqual(446, json['poi'][0]['location']['y'])
        self.assertEqual(2, json['poi'][1]['status']['code'])
        self.assertEqual("DISABLED", json['poi'][1]['status']['msg'])
        self.assertEqual(0, json['poi'][1]['mean_error'])
        self.assertEqual(446, json['poi'][1]['location']['x'])
        self.assertEqual(113, json['poi'][1]['location']['y'])
