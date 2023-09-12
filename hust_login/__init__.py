from .login import HustLogin, CheckLoginStatu
from ._HustPass import HustPass, HustPass_NotLoged

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("hust_login")
except PackageNotFoundError:
    __version__ = "unknown version"