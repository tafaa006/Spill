class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.smooth_speed = 0.1
        self.zoom_speed = 0.05
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target_x, target_y):
        self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed
        tx = target_x - (self.screen_width / 2) / self.zoom
        ty = target_y - (self.screen_height / 2) / self.zoom
        self.x += (tx - self.x) * self.smooth_speed
        self.y += (ty - self.y) * self.smooth_speed

    def apply(self, ex, ey):
        return (ex - self.x) * self.zoom, (ey - self.y) * self.zoom

    def apply_rect(self, rect):
        r = rect.copy()
        r.x = (rect.x - self.x) * self.zoom
        r.y = (rect.y - self.y) * self.zoom
        r.width = rect.width * self.zoom
        r.height = rect.height * self.zoom
        return r

    def zoom_in(self):
        self.target_zoom = min(2.0, self.target_zoom + 0.1)

    def zoom_out(self):
        self.target_zoom = max(0.5, self.target_zoom - 0.1)

    def reset(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0