from dls_imagematch.util.config import Config, IntConfigItem, DirectoryConfigItem, EnumConfigItem

from dls_imagematch.match import FeatureMatcher


class FocusConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        add = self.add

        methods = FeatureMatcher.DETECTOR_TYPES
        adapt = FeatureMatcher.ADAPTATION_TYPE

        self.align_method = add(EnumConfigItem, "Alignment Method", default="SURF", extra_arg=methods)
        self.align_adapt = add(EnumConfigItem, "Alignment Adaption", default="", extra_arg=adapt)
        self.kernel_size = add(IntConfigItem, "Laplacian Kernel Size", default=5, extra_arg='px')
        self.blur_radius = add(IntConfigItem, "Laplacian Blur Radius", default=5, extra_arg='px')
        self.input_dir = add(DirectoryConfigItem, "Input Directory", default="../test-images/focus/ring/")
        self.output_dir = add(DirectoryConfigItem, "Output Directory", default="../test-output/focus/")

        self.initialize_from_file()