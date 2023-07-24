from .login import HustLogin, CheckLoginStatu
from . import curriculum # 课表相关归属在此命名空间下
from ._HustPass import HustPass
from . import free_room
from . import utility_bills as bills

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("hust_login")
except PackageNotFoundError:
    __version__ = "unknown version"