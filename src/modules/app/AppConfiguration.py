import pydantic
from modules.base.Configuration import *
from modules.base.Instances import *
from pydantic import BaseModel

@configuration
class AppConfiguration(BaseModel):
    """AppConfiguration"""

    device: DeviceConfiguration
    """Device configuration"""

    platforms: Optional[list[WithPlugins(PlatformConfiguration)]] #type: ignore
    """List of platforms"""

    actions: Optional[list[WithPlugins(ActionConfiguration)]] #type: ignore
    """List of actions (=outputs)"""

    sensors: Optional[list[WithPlugins(SensorConfiguration)]] #type: ignore
    """List of sensors (=inputs)"""
