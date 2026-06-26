#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RSI Live Player - Advanced player with infobar and zapping
Based on TV Garden Project
"""
from enigma import (
    eServiceReference,
    iPlayableService,
    eTimer
)
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.InfoBarGenerics import (
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarNotifications,
)
import time

from .rsi_api import RSIApi
from .youtube_helper import get_youtube_stream
from .helpers import get_screen_resolution


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


# ============ DETECT SCREEN RESOLUTION ============
screen_width, screen_height = get_screen_resolution()

if screen_width >= 2560:  # WQHD
    OVERLAY_WIDTH = 2560
    OVERLAY_HEIGHT_TOP = 70
    OVERLAY_HEIGHT_INFO = 80
    FONT_SIZE_TOP = 42
    FONT_SIZE_INFO = 36
    OVERLAY_Y_INFO = screen_height - 100
    OVERLAY_Y_TOP = 10
elif screen_width >= 1920:  # FHD
    OVERLAY_WIDTH = 1920
    OVERLAY_HEIGHT_TOP = 60
    OVERLAY_HEIGHT_INFO = 70
    FONT_SIZE_TOP = 36
    FONT_SIZE_INFO = 32
    OVERLAY_Y_INFO = screen_height - 80
    OVERLAY_Y_TOP = 5
else:  # HD (1280x720) or lower
    OVERLAY_WIDTH = 1280
    OVERLAY_HEIGHT_TOP = 50
    OVERLAY_HEIGHT_INFO = 60
    FONT_SIZE_TOP = 28
    FONT_SIZE_INFO = 24
    OVERLAY_Y_INFO = screen_height - 70
    OVERLAY_Y_TOP = 0


class RsiInfoBarShowHide():
    """InfoBar show/hide control with top overlay management"""
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(
            ["InfobarShowHideActions"],
            {
                "toggleShow": self.OkPressed,
                "hide": self.hide
            },
            0
        )
        self.__event_tracker = ServiceEventTracker(
            screen=self, eventmap={
                iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0

        # ----- TOP OVERLAY: Controls help -----
        self.helpOverlay = Label("")
        self.helpOverlay.skinAttributes = [
            ("position", "0,0"),
            ("size", f"{screen_width},50"),
            ("font", "Regular;28"),
            ("halign", "center"),
            ("valign", "center"),
            ("foregroundColor", "#FFFFFF"),
            ("backgroundColor", "#80000000"),
            ("transparent", "0"),
            ("zPosition", "100")
        ]
        self["helpOverlay"] = self.helpOverlay
        self["helpOverlay"].hide()

        # ----- TOP-LEFT INFO: Video title and index -----
        self.infoOverlay = Label("")
        self.infoOverlay.skinAttributes = [
            ("position", "20,55"),
            ("size", f"{screen_width - 40},40"),
            ("font", "Regular;24"),
            ("halign", "left"),
            ("valign", "center"),
            ("foregroundColor", "#FFFF00"),
            ("backgroundColor", "#80000000"),
            ("transparent", "0"),
            ("zPosition", "100")
        ]
        self["infoOverlay"] = self.infoOverlay
        self["infoOverlay"].hide()

        # Timer to hide overlays after 5 seconds
        self.hideTimer = eTimer()
        try:
            self.hideTimer.timeout.connect(self.doTimerHide)
        except BaseException:
            self.hideTimer.callback.append(self.doTimerHide)

        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def get_current_channel_info(self):
        """Override in child class"""
        if hasattr(self, 'channel_list') and hasattr(self, 'current_index'):
            if self.channel_list and 0 <= self.current_index < len(
                    self.channel_list):
                channel = self.channel_list[self.current_index]
                name = channel.get('name', 'N/A')
                index = self.current_index + 1
                total = len(self.channel_list)
                return f"▶ {name} [{index}/{total}]"
        return "RSI Live Player"

    def show_overlays(self):
        """Show both overlays and start hide timer"""
        try:
            controls = "OK = Info | CH+/CH- = Next/Prev | STOP = Exit | by Lululla"
            info = self.get_current_channel_info()

            self["helpOverlay"].setText(controls)
            self["helpOverlay"].show()

            self["infoOverlay"].setText(info)
            self["infoOverlay"].show()

            self.hideTimer.start(5000, True)
        except Exception as e:
            print(f"[RSILive] Error showing overlays: {e}")

    def hide_overlays(self):
        """Hide both overlays and stop timer"""
        self.hideTimer.stop()
        if self["helpOverlay"].visible:
            self["helpOverlay"].hide()
            self["infoOverlay"].hide()

    def OkPressed(self):
        """Toggle overlays on OK press"""
        if self["helpOverlay"].visible:
            self.hide_overlays()
        else:
            self.show_overlays()
        self.toggleShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doHide(self):
        self.hideTimer.stop()
        self.hide()
        self.hide_overlays()
        self.startHideTimer()

    def serviceStarted(self):
        if self.execing:
            self.doShow()
            self.show_overlays()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            self.hideTimer.start(5000, True)

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()
            self.hide_overlays()

    def toggleShow(self):
        if not self.skipToggleShow:
            if self.__state == self.STATE_HIDDEN:
                self.doShow()
                self.show_overlays()
            else:
                self.doHide()
                self.hide_overlays()
        else:
            self.skipToggleShow = False

    def lockShow(self):
        try:
            self.__locked += 1
        except BaseException:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except BaseException:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()


class RsiPlayer(
        InfoBarBase,
        InfoBarSeek,
        InfoBarAudioSelection,
        InfoBarNotifications,
        RsiInfoBarShowHide,
        Screen):
    """Full-featured RSI player with infobar and zapping"""

    def __init__(self, session, channel_list=None, current_index=0):
        print("[RSILive DEBUG] RsiPlayer __init__ START")
        print("[RSILive DEBUG] channel_list: {}".format(channel_list))
        print("[RSILive DEBUG] current_index: {}".format(current_index))

        Screen.__init__(self, session)
        self.session = session
        self.channel_list = channel_list if channel_list else []
        print("[RSILive DEBUG] self.channel_list length: {}".format(
            len(self.channel_list)))
        self.skinName = 'MoviePlayer'

        self.api = RSIApi()
        self.current_index = current_index
        self.itemscount = len(self.channel_list)
        self.stream_running = False
        self.eof_count = 0
        self.last_eof_time = 0
        self.current_service = None

        InfoBarBase.__init__(self)
        InfoBarSeek.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarNotifications.__init__(self)
        RsiInfoBarShowHide.__init__(self)

        print("[RSILive] Player: {} channels, index {}".format(
            self.itemscount, self.current_index))

        self['actions'] = ActionMap(
            [
                'MoviePlayerActions',
                'MovieSelectionActions',
                'MediaPlayerActions',
                'EPGSelectActions',
                'OkCancelActions',
                'InfobarShowHideActions',
                'InfobarActions',
                'DirectionActions',
                'InfobarSeekActions'
            ],
            {
                "stop": self.leave_player,
                "cancel": self.leave_player,
                "back": self.leave_player,
                "info": self.show_channel_info,
                "channelDown": self.previous_channel,
                "channelUp": self.next_channel,
                "down": self.previous_channel,
                "up": self.next_channel,
            },
            -1
        )

        self.__event_tracker = ServiceEventTracker(
            screen=self,
            eventmap={
                iPlayableService.evStart: self.__serviceStarted,
                iPlayableService.evEOF: self.__evEOF,
                iPlayableService.evStopped: self.__evStopped,
            }
        )
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()

        # Timer for EOF recovery
        self.eof_recovery_timer = eTimer()
        try:
            self.eof_recovery_timer.timeout.connect(self.restartAfterEOF)
        except BaseException:
            self.eof_recovery_timer.callback.append(self.restartAfterEOF)

        # Timer for audio reset
        self.audio_reset_timer = eTimer()
        try:
            self.audio_reset_timer.timeout.connect(self.reset_audio_tracks)
        except BaseException:
            self.audio_reset_timer.callback.append(self.reset_audio_tracks)

        self.onFirstExecBegin.append(self.start_stream)
        self.onClose.append(self.cleanup)

    def get_current_channel_info(self):
        """Override for RsiInfoBarShowHide"""
        if self.channel_list and 0 <= self.current_index < len(
                self.channel_list):
            channel = self.channel_list[self.current_index]
            name = channel.get('name', 'N/A')
            index = self.current_index + 1
            total = self.itemscount
            return "{} [{}/{}]".format(name, index, total)
        return "RSI Live Player"

    def start_stream(self):
        if not self.channel_list:
            print("[RSILive] No channel list!")
            return

        current_channel = self.channel_list[self.current_index]
        stream_url = current_channel.get(
            'stream_url') or current_channel.get('url')
        channel_name = current_channel.get('name', 'RSI Channel')

        if not stream_url:
            print(
                "[RSILive] No stream URL for channel {}".format(
                    self.current_index))
            return

        print("[RSILive] Playing: {} - {}".format(channel_name,
              stream_url[:80] + "..."))

        # YouTube detection
        if "youtube.com" in stream_url or "youtu.be" in stream_url:
            print("[RSILive] YouTube detected, resolving...")
            resolved = get_youtube_stream(stream_url)
            if resolved:
                stream_url = resolved
                print("[RSILive] YouTube resolved OK")
            else:
                print("[RSILive] YouTube resolution failed")
                self.show_error_message("YouTube stream not available")
                return

        # Ensure stream_url is valid
        if not stream_url or not stream_url.startswith(
                ("http://", "https://")):
            print("[RSILive] Invalid stream URL: {}".format(stream_url))
            self.show_error_message("Invalid stream URL")
            return

        self.stream_running = True
        self.eof_count = 0

        try:
            # Determine service type (like WorldCam)
            if '.m3u8' in stream_url.lower():
                service_type = 5001  # HLS
            else:
                service_type = 4097  # HTTP

            # Build service reference
            url_encoded = stream_url.replace(":", "%3a")
            name_encoded = channel_name.replace(":", "%3a")

            ref_str = "{}:0:0:0:0:0:0:0:0:0:{}:{}".format(
                service_type, url_encoded, name_encoded)
            print("[RSILive DEBUG] Service ref: {}".format(ref_str[:200]))

            sref = eServiceReference(ref_str)
            sref.setName(channel_name)

            self.session.nav.playService(sref)
            self.current_service = sref

            # Show overlays
            self.show_overlays()

        except Exception as e:
            print("[RSILive] ERROR starting stream: {}".format(e))
            self.stream_running = False
            self.show_error_message("Cannot play: " + channel_name)

    def stop_stream(self):
        """Stop the current stream"""
        if self.stream_running:
            self.stream_running = False
            try:
                self.session.nav.stopService()
            except BaseException:
                pass

    def restartAfterEOF(self):
        """Restart stream after End-Of-File"""
        try:
            print("[RSILive] Restarting stream after EOF")
            self.stop_stream()
            time.sleep(0.5)
            self.start_stream()
        except Exception as e:
            print("[RSILive] Error restarting after EOF: {}".format(e))

    def next_channel(self):
        if self.itemscount <= 1:
            return
        self.stop_stream()
        self.current_index = (self.current_index + 1) % self.itemscount
        self.start_stream()

    def previous_channel(self):
        if self.itemscount <= 1:
            return
        self.stop_stream()
        self.current_index = (self.current_index - 1) % self.itemscount
        self.start_stream()

    def reset_audio_tracks(self):
        """Reset audio tracks after channel change"""
        try:
            service = self.session.nav.getCurrentService()
            if service:
                audio = service.audioTracks()
                if audio and audio.getNumberOfTracks() > 0:
                    audio.selectTrack(0)
                    print("[RSILive] Audio reset OK")
        except Exception as e:
            print("[RSILive] Audio reset error: {}".format(e))

    def show_channel_info(self):
        """Display info for the current channel"""
        if self.channel_list and 0 <= self.current_index < len(
                self.channel_list):
            channel = self.channel_list[self.current_index]
            info = "Channel: {}\n".format(channel.get('name', 'N/A'))
            info += "Index: {}/{}\n".format(
                self.current_index + 1, self.itemscount)
            if channel.get('country'):
                info += "Country: {}\n".format(channel.get('country'))
            if channel.get('language'):
                info += "Language: {}\n".format(channel.get('language'))
            url = channel.get('stream_url') or channel.get('url', 'N/A')
            info += "URL: {}".format(url[:80] +
                                     "..." if len(url) > 80 else url)
            self.session.open(MessageBox, info, MessageBox.TYPE_INFO)

    def show_error_message(self, message):
        """Show error message box"""
        self.session.open(MessageBox, message, MessageBox.TYPE_ERROR)

    def __serviceStarted(self):
        print("[RSILive] Playback started successfully")
        self.stream_running = True

    def __evEOF(self):
        """End of file reached"""
        print("[RSILive] End of stream (EOF)")

        current_time = time.time()
        if current_time - self.last_eof_time < 10:
            self.eof_count += 1
        else:
            self.eof_count = 1
        self.last_eof_time = current_time

        if self.eof_count <= 3:
            delay = 2 + (self.eof_count * 2)
            print("[RSILive] Restarting in {}s (attempt {}/3)".format(
                delay, self.eof_count))
            self.eof_recovery_timer.start(delay * 1000, True)
        else:
            print("[RSILive] Too many EOFs, stopping")
            self.leave_player()

    def __evStopped(self):
        print("[RSILive] Playback stopped")
        self.stream_running = False
        self.close()

    def cleanup(self):
        """Clean up resources and restore initial service"""
        self.eof_recovery_timer.stop()
        self.audio_reset_timer.stop()
        self.stop_stream()

        # Restore initial service
        if self.srefInit:
            try:
                self.session.nav.playService(self.srefInit)
            except BaseException:
                pass

    def leave_player(self):
        """Exit the player"""
        self.cleanup()
        self.close()
