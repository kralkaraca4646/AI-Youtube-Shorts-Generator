import os
from PIL import Image, ImageDraw, ImageFont

# Pillow 10+ sürüm uyumluluk yaması
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

class MoviePySubtitleGenerator:
    @staticmethod
    def create_text_clip_image(words_group, active_word_index, img_size=(1080, 1920)):
        img = Image.new("RGBA", img_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Font bulma
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        for p in [
            "/usr/share/fonts/truetype/custom/Montserrat-Bold.ttf",
            "/usr/share/fonts/opentype/montserrat/Montserrat-Bold.ttf",
            "/usr/share/fonts/truetype/fonts-montserrat/Montserrat-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]:
            if os.path.exists(p):
                font_path = p
                break
        
        try:
            font = ImageFont.truetype(font_path, size=75)
        except:
            font = ImageFont.load_default()

        text_full = " ".join([w['word'].upper() for w in words_group])
        
        try:
            bbox = draw.textbbox((0, 0), text_full, font=font)
            text_w = bbox[2] - bbox[0]
        except:
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
            except:
                current_x += 150

        return img
