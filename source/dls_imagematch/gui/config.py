from os.path import join

from dls_util.config.config import Config
from dls_util.config.item import DirectoryConfigItem
from dls_util.config.item_colour import ColorConfigItem
from dls_util.imaging import Color


class GuiConfig(Config):
    """ Configuration class that contains a number of options for the program. Stores options in a config
    file that can be edited externally to set the values of the options.
    """
    def __init__(self, config_directory):
        Config.__init__(self, join(config_directory, "gui.ini"))

        add = self.add

        self.set_title("Crystal Matching GUI Configuration")
        self.set_comment("Configuration for the program GUI including displayed colors and input/output directories.")

        self.color_align = add(ColorConfigItem, "Align Color", Color.purple())
        self.color_align.set_comment("Outline color displayed in GUI to indicate alignment overlap of two images.")

        self.color_search = add(ColorConfigItem, "Search Box Color", Color.orange())
        self.color_search.set_comment("Outline color displayed in GUI to indicate region to be searched for feature "
                                      "matching in second image.")

        self.color_crystal_image1 = add(ColorConfigItem, "Image1 Crystal Color", Color.green())
        self.color_crystal_image1.set_comment("Color displayed in GUI to indicate the position of the user selected "
                                              "points in the first image")

        self.color_crystal_image2 = add(ColorConfigItem, "Image2 Crystal Color", Color.red())
        self.color_crystal_image2.set_comment("Color displayed in GUI to indicate the position of the points in the "
                                              "second image calculated by feature matching.")

        self.input_dir = add(DirectoryConfigItem, "Input Directory", default="../test-images/")
        self.input_dir.set_comment("Directory for storing any files required by testing.")

        self.samples_dir = add(DirectoryConfigItem, "Samples Directory", default="../test-images/Formulatrix/")
        self.samples_dir.set_comment("Directory storing images taken for Formulatrix for testing.")

        self.output_dir = add(DirectoryConfigItem, "Output Directory", default="../test-output/")
        self.output_dir.set_comment("Directory for storing any files generated by testing.")

        self.config_dir = add(DirectoryConfigItem, "Config Directory", default=config_directory)
        self.config_dir.set_comment("Directory in which Detector configuration files are stored.")

        self.initialize_from_file()
