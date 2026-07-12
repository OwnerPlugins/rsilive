from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
import json
import os
import subprocess
import threading
import time

from .player import RsiPlayer
from .rsi_api import RSIApi
from .helpers import load_skin, PLUGIN_PATH, find_executable
from . import __version__, paypal

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


class RsiMain(Screen):
    def __init__(self, session):
        self.session = session
        self.api = RSIApi()
        self.loading_thread = None
        self.stop_loading = False

        self.nav_stack = []
        self.current_level = 0

        self.skin = load_skin("main")
        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.on_ok,
            "cancel": self.on_cancel
        })

        self["list"] = MenuList([])
        self["title"] = Label("RSI Play TV")
        self["version_label"] = Label(f"v.{__version__}")
        self["author_label"] = Label(paypal())

        self.onLayoutFinish.append(self.build_main_menu)
        self.onClose.append(self.stop_background_thread)

    def stop_background_thread(self):
        self.stop_loading = True
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1)

    def push_level(self, items, title=None):
        """Push a new level onto the navigation stack"""
        self.nav_stack.append(
            (self["list"].list,
             self["title"].getText()))
        self["list"].setList(items)
        if title:
            self["title"].setText(title)
        self.current_level += 1

    def pop_level(self):
        """Pop to previous level"""
        if self.nav_stack:
            prev_list, prev_title = self.nav_stack.pop()
            self["list"].setList(prev_list)
            self["title"].setText(prev_title)
            self.current_level -= 1
            return True
        return False

    def on_cancel(self):
        """Handle cancel/back button"""
        if self.current_level > 0:
            self.pop_level()
        else:
            self.close()

    def build_main_menu(self):
        """Main menu with categories"""
        categories = [
            {"name": "📺 YouTube Channels", "type": "category", "category": "youtube"},
            {"name": "📡 Live TV", "type": "category", "category": "live"}
        ]
        items = [(cat["name"], cat) for cat in categories]
        self["list"].setList(items)
        self["title"].setText("RSI Play TV")
        print("[RSILive] Main menu loaded")

    def on_ok(self):
        selection = self["list"].getCurrent()
        if not selection:
            return
        title, data = selection

        if data.get("type") == "category":
            self.open_category(data["category"])
            return

        stream_url = data.get('stream_url', '')

        # If it's a YouTube channel (not a video), show video list
        if 'youtube.com/channel/' in stream_url or 'youtube.com/@' in stream_url:
            self.show_channel_videos(data)
            return

        # --- VIDEO PLAYBACK WITH ZAPPING ---
        # Get the full list from current level
        full_list = self["list"].list
        if not full_list:
            self.session.open(RsiPlayer, [data], 0)
            return

        # Find index of selected item
        current_index = 0
        for i, item in enumerate(full_list):
            if item[0] == title and item[1] == data:
                current_index = i
                break

        # Extract channel data (data_dict) from each item
        channel_list = [item[1] for item in full_list]

        print(
            f"[RSILive] Playing video {current_index + 1}/{len(channel_list)}")
        self.session.open(RsiPlayer, channel_list, current_index)

    def open_category(self, category_name):
        if category_name == "youtube":
            self.show_youtube_channels()
        elif category_name == "live":
            self.show_live_channels()

    def show_youtube_channels(self):
        channels = []
        json_path = os.path.join(PLUGIN_PATH, "data", "youtube_channels.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict) and "channels" in data:
                    items = data["channels"]
                else:
                    items = []

                for channel in items:
                    name = channel.get('name', 'Unknown')
                    if 'url' in channel:
                        url = channel['url']
                    elif 'channel' in channel:
                        url = "https://www.youtube.com/channel/{}".format(
                            channel['channel'])
                    else:
                        continue
                    channels.append({
                        'name': name,
                        'stream_url': url,
                        'country': 'YouTube',
                        'language': 'Multi'
                    })

        items = [(ch["name"], ch) for ch in channels]
        self.push_level(items, "YouTube Channels")
        print(f"[RSILive] Loaded {len(channels)} YouTube channels")

    def show_live_channels(self):
        livestreams = self.api.get_livestreams()
        channels = []
        for name, url in livestreams.items():
            channels.append({
                'name': name,
                'stream_url': url,
                'country': 'Switzerland',
                'language': 'Italian'
            })
        items = [(ch["name"], ch) for ch in channels]
        self.push_level(items, "Live TV")
        print(f"[RSILive] Loaded {len(channels)} live channels")

    def show_channel_videos(self, channel_data):
        """Load videos from YouTube channel with background threading"""
        channel_url = channel_data['stream_url']
        channel_name = channel_data['name']

        # Push a loading level
        self.push_level([("Loading videos...", {})], channel_name)

        # Stop any previous thread
        self.stop_loading = True
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1)

        # Start new thread
        self.stop_loading = False
        self.loading_thread = threading.Thread(
            target=self._load_videos_worker,
            args=(channel_url, channel_name)
        )
        self.loading_thread.daemon = True
        self.loading_thread.start()

    def _load_videos_worker(self, channel_url, channel_name):
        """Background worker to load videos in batches"""
        ytdlp = find_executable("yt-dlp")
        if not ytdlp:
            self._update_video_list([("yt-dlp not found", {})])
            return

        all_videos = []
        batch_size = 20
        page = 0

        while not self.stop_loading:
            try:
                start = page * batch_size

                # 1. Get URLs
                url_cmd = [
                    ytdlp,
                    "--flat-playlist",
                    "--playlist-start", str(start + 1),
                    "--playlist-end", str(start + batch_size),
                    "--print", "url",
                    channel_url
                ]
                print(
                    f"[RSILive] Fetching batch {page + 1} (videos {start + 1}-{start + batch_size})")

                url_result = subprocess.run(
                    url_cmd, capture_output=True, text=True, timeout=30)
                if url_result.returncode != 0:
                    print(f"[RSILive] yt-dlp error: {url_result.stderr[:100]}")
                    break

                urls = [line.strip() for line in url_result.stdout.split(
                    '\n') if line.strip().startswith('http')]
                if not urls:
                    print("[RSILive] No URLs in this batch, stopping")
                    break

                # 2. Get titles
                title_cmd = [
                    ytdlp,
                    "--flat-playlist",
                    "--playlist-start", str(start + 1),
                    "--playlist-end", str(start + batch_size),
                    "--print", "title",
                    channel_url
                ]
                title_result = subprocess.run(
                    title_cmd, capture_output=True, text=True, timeout=30)
                titles = [
                    line.strip() for line in title_result.stdout.split('\n') if line.strip()]

                # 3. Combine
                batch_videos = []
                for i, url in enumerate(urls):
                    title = titles[i] if i < len(
                        titles) else f"Video {start + i + 1}"
                    batch_videos.append(
                        (title, {'name': title, 'stream_url': url}))

                if not batch_videos:
                    break

                all_videos.extend(batch_videos)
                print(f"[RSILive] Loaded {len(all_videos)} videos so far")
                self._update_video_list(all_videos)

                if len(urls) < batch_size:
                    print("[RSILive] Less than batch_size, stopping")
                    break

                page += 1
                time.sleep(0.5)

            except subprocess.TimeoutExpired:
                print("[RSILive] Timeout, stopping")
                break
            except Exception as e:
                print(f"[RSILive] Error: {e}")
                break

        if not all_videos and not self.stop_loading:
            self._update_video_list([("No videos found", {})])

    def _update_video_list(self, video_list):
        """Update the list widget from background thread"""
        from enigma import eTimer

        def update_ui():
            if not self.stop_loading and self.current_level > 0:
                self["list"].setList(video_list)
                print(f"[RSILive] UI updated with {len(video_list)} items")

        # Try callWithCallback first (preferred method)
        try:
            self.session.callWithCallback(update_ui, ())
        except AttributeError:
            # Fallback: eTimer
            timer = eTimer()
            timer.callback.append(update_ui)
            timer.start(0, True)

            # Keep timer alive
            if not hasattr(self, '_update_timers'):
                self._update_timers = []
            self._update_timers.append(timer)

    def _safe_ui_update(self, video_list):
        """Execute UI update in main thread"""
        def update_ui():
            if not self.stop_loading:
                if self.current_level > 0:
                    self["list"].setList(video_list)
                    print(f"[RSILive] UI updated with {len(video_list)} items")

        # Try session.callWithCallback first (most reliable)
        if hasattr(self.session, 'callWithCallback'):
            self.session.callWithCallback(update_ui, ())
        else:
            # Fallback to eTimer
            from enigma import eTimer
            timer = eTimer()
            timer.callback.append(update_ui)
            timer.start(0, True)
            # Keep timer alive by storing it
            self._update_timer = timer
