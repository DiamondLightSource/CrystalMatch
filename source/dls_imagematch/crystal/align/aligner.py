import logging

from dls_imagematch.crystal.align.sized_image import SizedImage
from dls_imagematch.feature import FeatureMatcher
from dls_util.shape import Point
from .aligned_images import AlignedImages
from .exception import ImageAlignmentError


class ImageAligner:

    def __init__(self, image1, image2, align_config, detector_config=None):
        """
        Takes two images and uses feature detection to provide a best fit alignment. The scale of the images will be
        normalized by resizing image1 to the same resolution as image2.  Note that this does not mean the images
        will be the same size!
        :param image1: This image will be rescaled to the same resolution as image2.
        :param image2: The image used to align the sample.
        :param align_config: Configuration object for this process.
        :param detector_config: Configuration object for the feature detector.
        """
        assert(align_config is not None)
        # Create images with associated real sizes
        px_size_1 = align_config.pixel_size_1.value()
        px_size_2 = align_config.pixel_size_2.value()
        self._resolution = px_size_2  # The resolution of the second resolution will be the working image
        self._scale_factor = px_size_1 / px_size_2

        logging.info("Image 1 original size: %d x %d (%d um/pixel)", image1.width(), image1.height(), px_size_1)
        logging.info("Image 2 original size: %d x %d (%d um/pixel)", image2.width(), image2.height(), px_size_2)
        logging.info("Scale Factor calculated as " + str(self._scale_factor))

        self._image1 = SizedImage.from_image(image1, px_size_1)
        self._image2 = SizedImage.from_image(image2, px_size_2)

        self._align_config = align_config
        self._detector_config = detector_config

        self._rescale_image_1()

    # -------- CONFIGURATION -------------------
    def set_align_config(self, config):
        self._align_config = config

    def set_detector_config(self, config):
        self._detector_config = config

    def _rescale_image_1(self):
        # Resize image A so it has the same size per pixel as image B
        if self._scale_factor != 1:
            self._image1 = self._image1.rescale(self._scale_factor)
            logging.info("Rescaling image 1 by scale factor " + str(self._scale_factor) +
                         ", new size: %d x %d", self._image1.width(), self._image1.height())

    # -------- FUNCTIONALITY -------------------
    def align(self):
        """ Perform image alignment, returning an AlignedImages object. """
        self._check_config()

        if not self._align_config.use_alignment.value():
            return self._default_alignment()

        detector = self._get_detector()
        match_result = self._perform_match(detector)
        aligned_images = self._generate_alignment(match_result, detector)

        return aligned_images

    def _default_alignment(self):
        """ Default alignment result with 0 offset. """
        translation = Point()
        description = "DISABLED!"
        return AlignedImages(self._image1, self._image2, self._resolution, self._scale_factor,
                             translation, self._align_config, description)

    def _check_config(self):
        """ Raises an exception if configuration has not been properly set. """
        if self._align_config is None:
            raise ImageAlignmentError("Must set Alignment config before performing alignment")
        elif self._detector_config is None:
            raise ImageAlignmentError("Must set Detector config before performing alignment")

    def _get_detector(self):
        """ Get the selected detector and raise and exception if it is disabled. """
        detector = self._align_config.align_detector.value()
        enabled = self._detector_config.is_detector_enabled(detector)
        if not enabled:
            raise ImageAlignmentError("Cannot perform image alignment as detector '{}' is disabled.".format(detector))

        return detector

    def _perform_match(self, detector):
        """ Perform feature matching between the two images. """
        matcher = FeatureMatcher(self._image1.to_mono(), self._image2.to_mono(), self._detector_config)
        matcher.set_detector(detector)
        match_result = matcher.match_translation_only()
        return match_result

    def _generate_alignment(self, match_result, detector):
        """ Generate a translation that maps image 2 to image 1 based on the feature match results. """
        if not match_result.has_transform():
            raise ImageAlignmentError("Image Alignment failed - no matches found.")

        translation = match_result.transform().translation()
        description = "Feature matching - " + detector
        aligned_images = AlignedImages(self._image1, self._image2, self._resolution, self._scale_factor,
                                       translation, self._align_config, description)
        aligned_images.feature_match_result = match_result
        return aligned_images
