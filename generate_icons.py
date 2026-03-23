"""Generate PWA icons for MoneyMap"""
import struct
import zlib

def create_png(width, height):
    """Create a simple PNG icon with a purple gradient background and $ symbol"""

    def make_pixel(x, y, w, h):
        # Gradient background - purple to indigo
        ratio_x = x / w
        ratio_y = y / h

        # Base gradient
        r = int(75 + ratio_x * 30 + ratio_y * 20)
        g = int(60 + ratio_x * 20)
        b = int(200 + ratio_x * 40 + ratio_y * 15)

        # Clamp
        r = min(max(r, 0), 255)
        g = min(max(g, 0), 255)
        b = min(max(b, 0), 255)

        # Draw $ symbol in white
        cx, cy = w // 2, h // 2
        size = w // 3

        # Dollar sign - simplified geometric shape
        dx = abs(x - cx)
        dy = y - cy

        # Vertical bar of $
        if dx <= size * 0.08 and abs(dy) <= size * 0.9:
            return (255, 255, 255, 255)

        # Top curve of S
        if -size * 0.7 <= dy <= -size * 0.15:
            ring_cx, ring_cy = cx, cy - int(size * 0.42)
            ring_r = size * 0.35
            dist = ((x - ring_cx) ** 2 + (y - ring_cy) ** 2) ** 0.5
            if ring_r - size * 0.12 <= dist <= ring_r + size * 0.12:
                # Only left half of top curve
                if x <= cx + size * 0.05 or (dy > -size * 0.25 and x <= cx + size * 0.3):
                    return (255, 255, 255, 255)

        # Bottom curve of S
        if size * 0.15 <= dy <= size * 0.7:
            ring_cx, ring_cy = cx, cy + int(size * 0.42)
            ring_r = size * 0.35
            dist = ((x - ring_cx) ** 2 + (y - ring_cy) ** 2) ** 0.5
            if ring_r - size * 0.12 <= dist <= ring_r + size * 0.12:
                # Only right half of bottom curve
                if x >= cx - size * 0.05 or (dy < size * 0.25 and x >= cx - size * 0.3):
                    return (255, 255, 255, 255)

        # Middle horizontal bar
        if abs(dy) <= size * 0.08 and dx <= size * 0.3:
            return (255, 255, 255, 255)

        return (r, g, b, 255)

    # Build raw pixel data
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter byte: None
        for x in range(width):
            r, g, b, a = make_pixel(x, y, width, height)
            raw_data.extend([r, g, b, a])

    # PNG file structure
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    signature = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    compressed = zlib.compress(bytes(raw_data), 9)

    return signature + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')


# Generate 192x192 and 512x512 icons
for size in [192, 512]:
    png_data = create_png(size, size)
    path = f"frontend/public/icons/icon-{size}.png"
    with open(path, 'wb') as f:
        f.write(png_data)
    print(f"Generated {path} ({len(png_data)} bytes)")
