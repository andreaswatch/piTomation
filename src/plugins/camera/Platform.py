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
        # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
        # all interfaces)
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', self.configuration.port))
        server_socket.listen(0)

        # Accept a single connection and make a file-like object out of it
        connection = server_socket.accept()[0].makefile('rb')
        try:
            while True:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                image_stream.write(connection.read(image_len))
                # Rewind the stream, open it as an image with PIL and do some
                # processing on it
                image_stream.seek(0)
                image = Image.open(image_stream)
                print('Image is %dx%d' % image.size)
                image.verify()
                print('Image is verified')
        finally:
            connection.close()
            server_socket.close()

    def dispose(self):
        return super().dispose()

   