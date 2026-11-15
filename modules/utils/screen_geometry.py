REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720


def is_widescreen(width, height):
    return width > 0 and height > 0 and width * 9 == height * 16


def to_native_point(x, y, width, height):
    """Map a point from the 720p reference to the actual game viewport."""
    if not is_widescreen(width, height):
        return x, y
    return x * width / REFERENCE_WIDTH, y * height / REFERENCE_HEIGHT
