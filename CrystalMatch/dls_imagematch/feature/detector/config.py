from os.path import join

from CrystalMatch.dls_util.config.config import Config
from CrystalMatch.dls_util.config.item import IntConfigItem, RangeIntConfigItem, FloatConfigItem, RangeFloatConfigItem, \
    EnumConfigItem, BoolConfigItem
from CrystalMatch.dls_imagematch.feature.detector.detector_orb import OrbDetector
from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType, ExtractorType


class DetectorConfig:
    def __init__(self, folder):
        self._folder = folder
        self.orb = OrbConfig(join(folder, "det_orb.ini"))


    def get_detector_options(self, detector):
        if detector == DetectorType.ORB:
            return self.orb
        else:
            raise ValueError("Unrecognised detector type")

class _BaseDetectorConfig(Config):
    def __init__(self, file_path, detector_type):
        Config.__init__(self, file_path)

        add = self.add
        det = detector_type

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.keypoint_limit = add(RangeIntConfigItem, "Keypoint Limit", det.DEFAULT_KEYPOINT_LIMIT, [1, 100])

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.keypoint_limit.set_comment(det.set_keypoint_limit.__doc__)


class OrbConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, OrbDetector)

        add = self.add
        det = OrbDetector

        self.set_title("ORB Detector Configuration")
        self.set_comment(det.__doc__)

        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES, [1, None])
        self.scale_factor = add(RangeFloatConfigItem, "Scale Factor", det.DEFAULT_SCALE_FACTOR, [1.001, None])
        self.n_levels = add(RangeIntConfigItem, "Num Levels", det.DEFAULT_N_LEVELS, [1, None])
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD, [1, None])
        self.first_level = add(RangeIntConfigItem, "First Level", det.DEFAULT_FIRST_LEVEL, [0, 0])
        self.wta_k = add(EnumConfigItem, "WTA_K", det.DEFAULT_WTA_K, det.WTA_K_VALUES)
        self.score_type = add(EnumConfigItem, "Score Type", det.DEFAULT_SCORE_TYPE, det.SCORE_TYPE_NAMES)
        self.patch_size = add(IntConfigItem, "Patch Size", det.DEFAULT_PATCH_SIZE, [2, None])

        self.n_features.set_comment(det.set_n_features.__doc__)
        self.scale_factor.set_comment(det.set_scale_factor.__doc__)
        self.n_levels.set_comment(det.set_n_levels.__doc__)
        self.edge_threshold.set_comment(det.set_edge_threshold.__doc__)
        self.first_level.set_comment(det.set_first_level.__doc__)
        self.wta_k.set_comment(det.set_wta_k.__doc__)
        self.score_type.set_comment(det.set_score_type.__doc__)
        self.patch_size.set_comment(det.set_patch_size.__doc__)

        self.initialize_from_file()

