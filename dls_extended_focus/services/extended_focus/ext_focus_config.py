import logging
from os.path import join

from dls_util.config.config import Config
from dls_util.config.item import StringItem, IntConfigItem, EnumConfigItem


class PlatformEnumConfigItem(object, EnumConfigItem):
    AUTO = "AUTO"
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    DETECTION_SETTINGS = [AUTO, WINDOWS, LINUX]

    def value(self):
        value = super(PlatformEnumConfigItem, self).value()
        if value is self.AUTO:
            return None
        else:
            return value == self.WINDOWS


class LogLevelEnumConfigItem(object, EnumConfigItem):
    ERROR = "ERROR"
    INFO = "INFO"
    DEBUG = "DEBUG"
    OFF = "OFF"
    LOG_LEVEL_SETTINGS = [ERROR, INFO, DEBUG, OFF]

    def value(self):
        value = super(LogLevelEnumConfigItem, self).value()
        if value is self.ERROR:
            return logging.ERROR
        elif value is self.INFO:
            return logging.INFO
        elif value is self.DEBUG:
            return logging.DEBUG
        else:
            return None


class ExtendedFocusConfig(Config):
    """
    Configuration file for the extended focus services. The service is designed to run a script to combine
    multiple images into a single image of optimum focus. It communicates over the network using the STOMP protocol.
    """
    CONFIG_FILE_NAME = "ext_focus_service.ini"

    def __init__(self, config_dir):
        self._config_dir = config_dir
        Config.__init__(self, join(config_dir, self.CONFIG_FILE_NAME))

        add = self.add

        self.set_title("Extended Focus Service Configuration File")
        self.set_comment("Configuration options for the Extended Focus Service which combines a stack of "
                         "images with different focal lengths into an optimum or extended-focus image.")

        self.host = add(StringItem, "Host", "localhost")
        self.host.set_comment("Address of the STOMP broker (Active MQ server or similar).")

        self.port = add(IntConfigItem, "Port", 61613)
        self.port.set_comment("Port number for the STOMP broker (Active MQ server or similar).")

        self.win_detect = add(EnumConfigItem, "Windows Detection",
                              PlatformEnumConfigItem.AUTO,
                              PlatformEnumConfigItem.DETECTION_SETTINGS)
        self.win_detect.set_comment("Allows the platform for the service to be set manually if auto-detection does "
                                    "not function.")

        self.win_net_prefix = add(StringItem, "Windows Network Prefix", "\\\\dc")
        self.win_net_prefix.set_comment("This service will be called from a Linux environment but may run on Windows.  "
                                        "If a Windows system is detected ")

        self.log_level = add(EnumConfigItem, "Log level", LogLevelEnumConfigItem.DEBUG, LogLevelEnumConfigItem.LOG_LEVEL_SETTINGS)
        self.log_level.set_comment("Sets the logging level")

        self.log_length = add(IntConfigItem, "Log length (hours)", 672)
        self.log_length.set_comment("Sets the length of log records - the default is 28 days")

        self.initialize_from_file()

    def parent_directory(self):
        return self._config_dir
