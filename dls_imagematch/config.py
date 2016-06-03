import os

from dls_imagematch.util import Color

DELIMITER = "="


class ConfigItem:
    OUTPUT_LINE = line = "{}" + DELIMITER + "{}\n"

    def __init__(self, tag, default):
        self._value = None
        self._tag = tag
        self._default = default

    def value(self):
        return self._value

    def set(self, value):
        self._value = self._clean(value)

    def tag(self):
        return self._tag

    def reset(self):
        self._value = self._default

    def output_line(self):
        return self.OUTPUT_LINE.format(self._tag, self._value)

    def _clean(self, value):
        return value

    def set_from_string(self, string):
        pass


class IntConfigItem(ConfigItem):
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def _clean(self, value):
        try:
            return int(value)
        except ValueError:
            return self._default

    def set_from_string(self, string):
        self._value = self._clean(string)


class DirConfigItem(ConfigItem):
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def _clean(self, value):
        value = str(value).strip()
        if not value.endswith("/"):
            value += "/"
        return value

    def set_from_string(self, string):
        self._value = self._clean(string)


class ColorConfigItem(ConfigItem):
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def set_from_string(self, string):
        self._value = Color.from_string(string)


class Config:
    def __init__(self, file):
        self._file = file
        self._items = []

        new = self._new_item

        self.region_size = new(IntConfigItem, "region_size", default=30)
        self.search_width = new(IntConfigItem, "search_width", default=200)
        self.search_height = new(IntConfigItem, "search_height", default=400)
        self.input_dir = new(DirConfigItem, "input_dir_root", default="../test-images/")
        self.samples_dir = new(DirConfigItem, "samples_dir", default="../test-images/Sample Sets/")
        self.output_dir = new(DirConfigItem, "output_dir", default="../test-output/")
        self.color_align = new(ColorConfigItem, "color_align", Color.Purple())
        self.color_search = new(ColorConfigItem, "color_search", Color.Orange())

        self.reset_all()

        self._load_from_file(file)

    def _new_item(self, cls, tag, default):
        item = cls(tag, default)
        self._items.append(item)
        return item

    def update_config_file(self):
        """ Save the options to the config file. """
        self._save_to_file(self._file)

    def reset_all(self):
        for item in self._items:
            item.reset()

    def _save_to_file(self, file):
        """ Save the options to the specified file. """
        with open(file, 'w') as f:
            for item in self._items:
                f.write(item.output_line())

    def _load_from_file(self, file):
        """ Load options from the specified file. """
        if not os.path.isfile(file):
            self._save_to_file(file)
            return

        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                try:
                    self._parse_line(line)
                except ValueError:
                    pass

    def _parse_line(self, line):
        """ Parse a line from a config file, setting the relevant option. """
        tokens = line.strip().split(DELIMITER)
        tag, value = tuple(tokens)
        for item in self._items:
            if tag == item.tag():
                item.set_from_string(value)
                break
