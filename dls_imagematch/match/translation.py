from dls_imagematch.util import Image


class Translation:
    def __init__(self, translation):
        self._translation = translation

    def translation(self):
        return self._translation

    def transform_image(self, image, output_size):
        offset = self._translation
        warped = Image.blank(output_size[0], output_size[1], image.channels)
        warped.paste(image, offset)
        return warped

    def inverse_transform_image(self, image, output_size):
        offset = - self._translation
        warped = Image.blank(output_size[0], output_size[1], image.channels)
        warped.paste(image, offset)
        return warped

    def transform_points(self, points):
        transformed = [p - self._translation for p in points]
        return transformed

    def inverse_transform_points(self, points):
        transformed = [p + self._translation for p in points]
        return transformed
