import os
from PIL import Image, ImageDraw, ImageFont

# Pillow 10+ sürüm uyumluluk yaması
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# Fontu repodan, sisteme bağımlı olmadan yükle.
# assets/fonts/Font.ttf dosyasını repoya eklemen gerekiyor (bkz. açıklama).
_FONT_PATH_BUNDLED = os.path.join(os.getcwd(), "assets", "fonts", "Font.ttf")

_FALLBACK_SYSTEM_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

_FONT_CACHE = {}


def _load_font(size=75):
    """
    Fontu önce repoya gömülü dosyadan, bulunamazsa sistem fontlarından
    yükler. Hiçbiri bulunamazsa açıkça uyarı basar (sessizce PIL'in
    ~10px'lik görünmez varsayılan fontuna düşmez).
    """
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]

    candidates = [_FONT_PATH_BUNDLED] + _FALLBACK_SYSTEM_FONTS

    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size=size)
                _FONT_CACHE[size] = font
                return font
            except Exception:
                continue

    print(
        "   🚨 UYARI: Hiçbir .ttf font dosyası bulunamadı! "
        "Altyazılar PIL'in minik varsayılan fontuyla (neredeyse görünmez) "
        "çizilecek. assets/fonts/Font.ttf ekleyerek bunu çöz."
    )
    font = ImageFont.load_default()
    _FONT_CACHE[size] = font
    return font


class MoviePySubtitleGenerator:
    @staticmethod
    def create_text_clip_image(words_group, active_word_index, img_size=(1080, 1920)):
        img = Image.new("RGBA", img_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font = _load_font(size=75)

        text_full = " ".join([w['word'].upper() for w in words_group])

        try:
            bbox = draw.textbbox((0, 0), text_full, font=font)
            text_w = bbox[2] - bbox[0]
        except Exception:
            text_w = 800

        x = (img_size[0] - text_w) / 2
        y = img_size[1] - 400

        current_x = x
        for i, w in enumerate(words_group):
            word_str = w['word'].upper() + " "
            is_active = (i == active_word_index)
            color = "#00FFFF" if is_active else "#FFFFFF"

            outline_color = "#000000"
            for adj_x in [-3, 0, 3]:
                for adj_y in [-3, 0, 3]:
                    draw.text((current_x + adj_x, y + adj_y), word_str, font=font, fill=outline_color)

            draw.text((current_x, y), word_str, font=font, fill=color)

            try:
                w_bbox = draw.textbbox((0, 0), word_str, font=font)
                current_x += (w_bbox[2] - w_bbox[0])
            except Exception:
                current_x += 150

        return img
