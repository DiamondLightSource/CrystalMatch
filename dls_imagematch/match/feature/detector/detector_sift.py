import cv2

from .types import DetectorType
from ..exception import FeatureDetectorError
from .detector import Detector


class SiftDetector(Detector):
    """
    See:
    http://docs.opencv.org/3.1.0/d5/d3c/classcv_1_1xfeatures2d_1_1SIFT.html
     or
    http://docs.opencv.org/2.4/modules/nonfree/doc/feature_detection.html
    """
    DEFAULT_N_FEATURES = 500
    DEFAULT_N_OCTAVE_LAYERS = 3
    DEFAULT_CONTRAST_THRESHOLD = 0.04
    DEFAULT_EDGE_THRESHOLD = 10
    DEFAULT_SIGMA = 1.6

    def __init__(self):
        Detector.__init__(self, DetectorType.SIFT)

        self._n_features = self.DEFAULT_N_FEATURES
        self._n_octave_layers = self.DEFAULT_N_OCTAVE_LAYERS
        self._contrast_threshold = self.DEFAULT_CONTRAST_THRESHOLD
        self._edge_threshold = self.DEFAULT_EDGE_THRESHOLD
        self._sigma = self.DEFAULT_SIGMA

    # -------- CONFIGURATION ------------------
    def set_n_features(self, value):
        """ The maximum number of features to retain. """
        if int(value) < 1:
            raise FeatureDetectorError("SIFT number of features must be positive integer")
        self._n_features = int(value)

    def set_octave_layers(self, value):
        """ The number of layers in each octave. 3 is the value used in D. Lowe paper. The number of octaves
        is computed automatically from the image resolution. """
        self._n_octave_layers = int(value)

    def set_contrast_threshold(self, value):
        """ The contrast threshold used to filter out weak features in semi-uniform (low-contrast) regions.
        The larger the threshold, the less features are produced by the detector. """
        self._contrast_threshold = float(value)

    def set_edge_threshold(self, value):
        """ The threshold used to filter out edge-like features. Note that the its meaning is different
        from the contrastThreshold, i.e. the larger the edgeThreshold, the less features are filtered out
        (more features are retained). """
        self._edge_threshold = int(value)

    def set_sigma(self, value):
        """ The sigma of the Gaussian applied to the input image at the octave #0. If your image is captured
        with a weak camera with soft lenses, you might want to reduce the number. """
        self._sigma = float(value)

    # -------- FUNCTIONALITY -------------------
    def _create_detector(self):
        print("Creating SIFT detector")
        detector = cv2.SIFT(nfeatures=self._n_features,
                            nOctaveLayers=self._n_octave_layers,
                            contrastThreshold=self._contrast_threshold,
                            edgeThreshold=self._edge_threshold,
                            sigma=self._sigma)

        return detector