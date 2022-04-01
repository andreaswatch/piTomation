import threading

from modules.base.Configuration import *
from modules.base.Instances import *

@configuration
class HttpdPlatformConfiguration(PlatformConfiguration):
    '''Configuration settings for the Httpd'''

    @validator('platform')
    def check_platform(cls, v):
        if "plugins.httpd" not in v:
            raise ValueError("wrong platform: plugins.httpd, is: " + v)
        return v

    port: int = 8001
    '''http port'''

    path: str = "/var/lib/www"
    '''path to serve'''

    secure: bool = False
    '''encrypt connection'''

    certfile: Optional[str] = ""
    '''path to cert file'''

    keyfile: Optional[str] = ""
    '''path to key file'''


class Platform(BasePlatform, Logging):
    '''This platform opens a serial console through the tx_pin to the Httpd.
    Use the Action to invoke commands like 'play'. 
    '''

    def __init__(self, parent: Stackable, config: HttpdPlatformConfiguration) -> None:
        super().__init__(parent, config)
        self.configuration = config

        try:
            from http.server import HTTPServer
            from http.server import SimpleHTTPRequestHandler
            import ssl
            import os

            def serve():
                os.chdir(self.configuration.path)

                Handler = SimpleHTTPRequestHandler
                server = HTTPServer(('', int(self.configuration.port)), Handler)
                if self.configuration.secure:
                    server.socket = ssl.wrap_socket(server.socket, 
                        certfile=self.configuration.certfile, 
                        keyfile=self.configuration.keyfile
                    )
                print("Serve on " + str(self.configuration.port))
                server.serve_forever()

            loop_thread = threading.Thread(target=serve)
            loop_thread.start()
            self.has_started = True
            
        except Exception as e:
            self.log_error(e)
