from Plugins.Plugin import PluginDescriptor
from .main import RsiMain
from . import __version__

"""
#############################################################
#  RSILive - RSI Play TV for Enigma2                        #
#  Created by: Lululla (https://github.com/OwnerPlugins)    #
#  Version: 1.0                                             #
#  License: GPLv3                                           #
#  Last Modified: 2026-06-26                                #
#############################################################

HELPERS MODULE - RSILive plugin

MAIN FEATURES:
• Screen resolution detection (HD/FHD/UHD)
• Dynamic skin loading based on resolution
• Executable path finder (yt-dlp, etc.)
• Cache directory management
• Plugin path constants
• File and directory utilities

FUNCTIONS:
• get_screen_resolution() - Returns (width, height) of Enigma2 desktop
• get_resolution_type() - Returns 'hd', 'fhd', or 'uhd' based on screen width
• load_skin(screen_name) - Loads skin XML for current resolution (fallback to HD)
• find_executable(name) - Searches PATH for executable
• get_cache_path(filename) - Returns path for cache files in /tmp
• ensure_dir(path) - Creates directory if it doesn't exist

USAGE:
    from .helpers import PLUGIN_PATH, load_skin, find_executable

    skin = load_skin("main")
    ytdlp = find_executable("yt-dlp")
    cache = get_cache_path("videos.json")

VERSION HISTORY:
v1.0 - Initial release with resolution detection and skin loading
#############################################################
"""


def main(session, **kwargs):
    session.open(RsiMain)


def Plugins(**kwargs):
    return [PluginDescriptor(
        name="RSILive",
        description="RSI Play TV v%s by Lululla" % __version__,
        icon="icon.png",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main
    )]
