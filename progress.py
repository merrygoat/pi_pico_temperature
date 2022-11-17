from ext.lcd import LCD


class ProgressIcon:
    def __init__(self, screen: LCD, x: int, y: int):
        self.position = 0
        self.x = x
        self.y = y
        self.base_col = 0xFFFF
        self.tick_col = 0xFF00

        self.coords = ((0, 0), (4, 0), (8, 0), (8, 4), (8, 8), (4, 8), (0, 8), (0, 4))
        for x_offset, y_offset in self.coords:
            screen.fill_rect(x + x_offset, y + y_offset, 3, 3, self.base_col)
        screen.show()

    def tick(self, screen: LCD):
        old_x_offset, old_y_offset = self.coords[self.position]
        self.position += 1
        if self.position == 8:
            self.position = 0
        x_offset, y_offset = self.coords[self.position]
        screen.fill_rect(self.x + old_x_offset, self.y + old_y_offset, 3, 3, self.base_col)
        screen.fill_rect(self.x + x_offset, self.y + y_offset, 3, 3, self.tick_col)