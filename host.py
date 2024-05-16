class VideoPlayer:
    def __init__(self, video_path):
        self.instance = Instance()
        self.media = self.instance.media_new(video_path)
        self.player: MediaPlayer = self.instance.media_player_new()
        self.player.set_media(self.media)
        self.fix = True
        self.video_path = video_path

    def hot_keys(self, event):
        active_window = getActiveWindow()
        if "VLC" in active_window.title:
            key = event.name.lower()
            match key:
                case "space":
                    self.player.pause()
                case "enter":
                    f_s = self.player.get_fullscreen()
                    self.player.set_fullscreen(not f_s)
                case "esc":
                    return self.finish()
                case "down" | "up":
                    self.set_volume(key)
                case "right" | "left":
                    self.set_seek(key)
                case "-":
                    return client.send_query(
                        "timeMatch", dict(
                            videotime=self.player.get_time(),
                            timestamp=time())
                    )
            if key == "*" or not self.fix:
                self.fix = not self.fix
            else:
                client.send_query("keyAction", dict(key=key))

    def action(self):
        self.player.play()
        on_press(self.hot_keys), wait()
        return self.finish()

    def finish(self):
        self.player.stop(), self.player.release(), exit()

    def set_time(self, ms):
        return self.player.set_time(int(int(ms)))

    def match_time(self, v: int, r: float):
        return self.player.set_time(
            v + int(round(time() - r, 3) * 1e3)
        )

    def set_seek(self, action='right', ms=5e3):
        if timestamp := self.player.get_time():
            try:
                return self.set_time(
                    timestamp + (1 if action == 'right' else -1) * ms
                )
            except:
                pass

    def set_volume(self, action='down'):
        volume = self.player.audio_get_volume()
        if (action == 'down' and volume > 0) or (action == 'up' and volume < 100):
            self.player.audio_set_volume(
                volume + (-1 if action == 'down' else 1) * 10
            )
