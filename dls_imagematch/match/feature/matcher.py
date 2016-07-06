from __future__ import division

import cv2

from .homography import MatchHomographyCalculator
from .match_result import FeatureMatchResult

from .exception import FeatureMatchException
from ._single_match import SingleFeatureMatch
from .detector import FeatureDetector


class FeatureMatcher:
    """ Use feature matching to compare two images and align the second on the first.

    Performs a feature matching operation between the two selected images (or image regions if
    specified. The resulting transformation can be applied to a point in Image/Region 1 coordinates
    to map it to its matching point in Image 2 coordinates.

    Note this only works correctly under OpenCV v2. Under v3, the function 'orb.detectAndCompute()'
    does not work properly for Python - it incorrectly raises an exception. This is a widely known
    and reported problem but it doesn't seem to have been fixed yet.
    """
    _MIN_MATCHES = 1
    _MAX_MATCHES = 200

    def __init__(self, img1, img2):
        """ Feature Matching between two images. If rectangular regions are provided, the routine will
        only consider features in those regions. """
        self._detector = FeatureDetector()

        self.img1 = img1
        self.img2 = img2

    def set_detector(self, method, adaptation=""):
        self._detector = FeatureDetector(method, adaptation)

    def match(self, translation_only=False):
        matches = self._find_matches()
        homography = MatchHomographyCalculator()
        transform = homography.calculate_transform(matches, translation_only)
        return self._create_result_object(matches, transform)

    def match_translation_only(self):
        return self.match(translation_only=True)

    def _create_result_object(self, matches, transform):
        result = FeatureMatchResult(self.img1, self.img2, matches, transform)
        result.method = self._detector.detector
        result.method_adapt = self._detector.adaptation
        return result

    def _find_matches(self):
        if self._detector.is_consensus_type():
            matches = self._find_matches_for_consensus()
        else:
            matches = self._find_matches_for_method(self._detector)

        if not self._has_minimum_number_of_matches(matches):
            self._raise_insufficient_matches_exception()

        return matches

    def _find_matches_for_consensus(self):
        matches = []
        for method in FeatureDetector.get_consensus_methods(self._detector.adaptation):
            try:
                method_matches = self._find_matches_for_method(method)
                matches.extend(method_matches)
            except FeatureMatchException:
                pass
        return matches

    def _find_matches_for_method(self, method):
        keypoints1, descriptors1 = method.detect_features(self.img1)
        keypoints2, descriptors2 = method.detect_features(self.img2)

        raw_matches = self._brute_force_match(method, descriptors1, descriptors2)
        matches = self._matches_from_raw(raw_matches, keypoints1, keypoints2, method)
        return matches

    def _matches_from_raw(self, raw_matches, keypoints1, keypoints2, method):
        matches = SingleFeatureMatch.matches_from_raw(raw_matches, keypoints1, keypoints2, method)
        return matches

    def _brute_force_match(self, method, descriptors_1, descriptors_2):
        """ For two sets of feature descriptors generated from 2 images, attempt to find all the matches,
        i.e. find features that occur in both images.
        """
        # TODO: Try out a FLANN based matcher
        if len(descriptors_1) == 0 or len(descriptors_2) == 0:
            return []

        matcher = cv2.BFMatcher(method.normalization_type(), crossCheck=True)
        matches = matcher.match(descriptors_1, descriptors_2)
        top_matches = sorted(matches, key=lambda x: x.distance)[:self._MAX_MATCHES]

        return top_matches

    def _has_minimum_number_of_matches(self, matches):
        return len(matches) >= self._MIN_MATCHES

    def _raise_insufficient_matches_exception(self):
        message = "Could not find the required minimum number of matches ({})!".format(self._MIN_MATCHES)
        raise FeatureMatchException(message)


class BoundedFeatureMatcher(FeatureMatcher):
    def __init__(self, img1, img2, img1_rect, img2_rect):
        """ Allows user to specify sub regions of the two images. When performing the matching operations,
        only features in these regions will be considered. """
        FeatureMatcher.__init__(self, img1, img2)

        if img1_rect is None:
            img1_rect = img1.bounds()

        if img2_rect is None:
            img2_rect = img2.bounds()

        self.img1 = img1.crop(img1_rect)
        self.img2 = img2.crop(img2_rect)

        self.img1_offset = img1_rect.top_left()
        self.img2_offset = img2_rect.top_left()

    def _matches_from_raw(self, raw_matches, keypoints1, keypoints2, method):
        matches = SingleFeatureMatch.matches_from_raw(raw_matches, keypoints1, keypoints2, method)
        for match in matches:
            match.set_offsets(self.img1_offset, self.img2_offset)

        return matches
