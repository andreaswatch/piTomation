from pydantic.class_validators import validator
from modules.base.Configuration import *
from modules.base.Instances import *
import io
import socket
import struct
from PIL import Image

@configuration
class CameraPlatformConfiguration(PlatformConfiguration):
    '''Allows to stream a camera.'''

    port: Optional[int] = 8091

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.camera" not in v:
            raise ValueError("wrong platform: plugins.camera, is: " + v)
        return v


class Platform(BasePlatform):
    '''Camera Platform'''

    def __init__(self, parent: Stackable, config: CameraPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

    def start(self, call_stack: CallStack):
        import picamera.picamera as pc
        pc.StartStream(self.configuration.port)
        pass

    def dispose(self):
        return super().dispose()

   