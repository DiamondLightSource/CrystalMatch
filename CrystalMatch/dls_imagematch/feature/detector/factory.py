from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError

from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType
from CrystalMatch.dls_imagematch.feature.detector.detector import Detector
from CrystalMatch.dls_imagematch.feature.detector.detector_orb import OrbDetector


class DetectorFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(det_type, options=None):
        if det_type not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("Unknown detector type: {}".format(det_type))

        if det_type == DetectorType.ORB:
            detector = OrbDetector()
        else:
            detector = Detector(detector=det_type)

        if options is not None:
            detector_options = options.get_detector_options(det_type)
            detector.set_from_config(detector_options)

        return detector

    @staticmethod
    def get_all_detectors(options=None):
        detectors = []

        for det in DetectorType.LIST_ALL:
            detector = DetectorFactory.create(det, options)
            detectors.append(detector)
        return detectors
