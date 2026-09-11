"""依存ライブラリなし(zlib/structのみ)でPWAアイコンPNGを生成するスクリプト。
ローソク足3本のシンプルなアイコンを描画する。
"""
import zlib
import struct


def make_png(width, height, pixels_rgba):
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (none)
        for x in range(width):
            r, g, b, a = pixels_rgba[y * width + x]
            raw += bytes((r, g, b, a))
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def draw_icon(size):
    bg = (15, 23, 32, 255)      # 濃紺背景
    green = (38, 194, 129, 255)  # 陽線
    red = (240, 84, 84, 255)     # 陰線
    wick = (170, 180, 195, 255)

    px = [bg] * (size * size)

    def set_px(x, y, color):
        if 0 <= x < size and 0 <= y < size:
            px[y * size + x] = color

    def rect(x0, y0, x1, y1, color):
        for y in range(y0, y1):
            for x in range(x0, x1):
                set_px(x, y, color)

    margin = int(size * 0.12)
    usable = size - margin * 2
    candle_w = int(usable * 0.16)
    gap = int(usable * 0.09)
    wick_w = max(2, int(size * 0.02))

    # 3本のローソク足: 陽線・陰線・陽線、高さと実体位置は見た目重視で手決め
    candles = [
        {"body_top": 0.55, "body_bot": 0.75, "wick_top": 0.45, "wick_bot": 0.82, "color": green},
        {"body_top": 0.30, "body_bot": 0.60, "wick_top": 0.20, "wick_bot": 0.68, "color": red},
        {"body_top": 0.15, "body_bot": 0.42, "wick_top": 0.08, "wick_bot": 0.50, "color": green},
    ]

    x = margin
    for c in candles:
        cx = x + candle_w // 2
        wy0 = margin + int(usable * c["wick_top"])
        wy1 = margin + int(usable * c["wick_bot"])
        rect(cx - wick_w // 2, wy0, cx + wick_w // 2, wy1, wick)

        by0 = margin + int(usable * c["body_top"])
        by1 = margin + int(usable * c["body_bot"])
        rect(x, by0, x + candle_w, by1, c["color"])

        x += candle_w + gap

    return px


for size in (512, 192, 180):
    pixels = draw_icon(size)
    data = make_png(size, size, pixels)
    out_path = f"icons/icon-{size}.png"
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"wrote {out_path} ({len(data)} bytes)")
