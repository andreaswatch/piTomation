import pydantic
from modules.app.base.Configuration import *
from modules.app.base.Instances import *
from pydantic import BaseModel

@configuration
class AppConfiguration(BaseModel):
    """AppConfiguration"""

    device: DeviceConfiguration
    """Device configuration"""

    platforms: Optional[list[WithPlugins(PlatformConfiguration)]]
    """List of platforms"""

    actions: Optional[list[WithPlugins(ActionConfiguration)]]
    """List of actions (=outputs)"""

    sensors: Optional[list[WithPlugins(SensorConfiguration)]]
    """List of sensors (=inputs)"""
