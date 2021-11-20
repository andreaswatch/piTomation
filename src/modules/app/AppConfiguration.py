from modules.base.Configuration import *
from modules.base.Instances import *


@configuration
class AppConfiguration(VariablesConfiguration):
    """AppConfiguration"""

    device: DeviceConfiguration
    """Device configuration"""

    platforms: Optional[list[WithPlugins(PlatformConfiguration)]] #type: ignore
    """List of platforms, see `plugins`"""

    actions: Optional[list[WithPlugins(ActionConfiguration)]] #type: ignore
    """List of actions (=outputs), see `plugins`"""

    sensors: Optional[list[WithPlugins(SensorConfiguration)]] #type: ignore
    """List of sensors (=inputs), see `plugins`"""
