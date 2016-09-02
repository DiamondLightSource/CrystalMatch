from feature.detector import DetectorType
from dls_imagematch.util.config import Config, EnumConfigItem, BoolConfigItem, RangeFloatConfigItem


class AlignConfig(Config):
    """ Configuration class that contains a number of options for the program. Stores options in a config
    file that can be edited externally to set the values of the options.
    """
    def __init__(self, config_directory):
        Config.__init__(self, config_directory + "align.ini")

        add = self.add

        self.set_title("Image Alignment Configuration")
        self.set_comment("Configuration for the initial image alignment process used in the crystal matching, "
                         "including the detector to be used and limits quantifying the quality of the alignment.")

        self.use_alignment = add(BoolConfigItem, "Perform Alignment", True)
        self.use_alignment.set_comment("Automatically perform bulk image alignment using feature matching when a new "
                                       "image is selected. If disabled, the images will just be lined up by the top "
                                       "left corner, which is fine if you know that the images are already lined up.")

        self.align_detector = add(EnumConfigItem, "Detector", default=DetectorType.ORB, extra_arg=DetectorType.LIST_ALL)
        self.align_detector.set_comment("Feature detection algorithm to be used for the initial image alignment "
                                        "process.")

        self.metric_limit_low = add(RangeFloatConfigItem, "Metric Limit Low", 15.0, [0.0, None])
        self.metric_limit_low.set_comment("A metric quantifying the quality of the alignment is calculated. If the "
                                          "metric is below this value, it is considered a good fit; if it is above, "
                                          "then the fit is considered poor.")

        self.metric_limit_high = add(RangeFloatConfigItem, "Metric Limit High", 25.0, [0.0, None])
        self.metric_limit_high.set_comment("A metric quantifying the quality of the alignment is calculated. If the "
                                           "metric is below this value, it is considered a poor fit; if it is above, "
                                           "then the fit is considered to have failed totally, i.e. the images are "
                                           "completely dissimilar.")

        self.initialize_from_file()
