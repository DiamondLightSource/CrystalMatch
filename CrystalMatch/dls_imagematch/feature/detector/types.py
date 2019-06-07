class DetectorType:
    def __init__(self):
        pass

    ORB = "ORB"
    BRISK = "BRISK"

    LIST_ALL = [ORB, BRISK]

class ExtractorType:
    def __init__(self):
        pass

    BRIEF = "BRIEF"
    ORB = "ORB"
    BRISK = "BRISK"

    LIST_ALL = [BRIEF, ORB, BRISK]

    @staticmethod
    def distance_factor(factor_type):
        """ Each extractor type has a different keypoint representation and so a different metric is used
        for calculating the match keypoint distance in each case. """
        return 1


class AdaptationType:
    def __init__(self):
        pass

    NONE = ""
    GRID = "Grid"
    PYRAMID = "Pyramid"

    LIST_ALL = [NONE, GRID, PYRAMID]
