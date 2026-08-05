import os
from PIL import Image, ImageDraw, ImageFont

class MoviePySubtitleGenerator:
    @staticmethod
    def create_text_clip_image(words_group, active_word_index, img_size=(1080, 1920)):
        """
        Kelime grubunu ve aktif olan kelimeyi sarı, diğerlerini beyaz yapacak şekilde 
        şeffaf bir PNG görseli (ImageClip) üretir.
        """
        img = Image.new("RGBA", img_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Linux sistemlerde (GitHub Actions) Montserrat fontunu arıyoruz, yoksa varsayılan kullanıyoruz
        font_path = "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf" # Yedek
        for p in [
            "/usr/share/fonts/truetype/custom/Montserrat-Bold.ttf",
            "/usr/share/fonts/opentype/montserrat/Montserrat-Bold.ttf",
            "/usr/share/fonts/truetype/fonts-montserrat/Montserrat-Bold.ttf"
        ]:
            if os.path.exists(p):
                font_path = p
                break
        
        try:
            font = ImageFont.truetype(font_path, size=75)
        except:
            font = ImageFont.load_default()

        # Metni oluştur (Tüm kelimeler büyük harf)
        text_full = " ".join([w['word'].upper() for w in words_group])
        
        # Metni ortalamak için boyut hesabı (Modern Pillow sürümleri için textbbox)
        try:
            bbox = draw.textbbox((0, 0), text_full, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except:
            text_w, text_h = 800, 100 # Fallback

        x = (img_size[0] - text_w) / 2
        y = img_size[1] - 400  # Ekranın alt kısmına yakın

        # Kelime kelime çizim (Aktif olan sarı, diğerleri beyaz + siyah kontur)
        current_x = x
        for i, w in enumerate(words_group):
            word_str = w['word'].upper() + " "
            is_active = (i == active_word_index)
            color = "#00FFFF" if is_active else "#FFFFFF" # Aktif Sarı, Pasif Beyaz
            
            # Siyah kontur (Outline etkisi için 4 yöne gölge)
            outline_color = "#000000"
            for adj_x in [-3, 0, 3]:
                for adj_y in [-3, 0, 3]:
                    draw.text((current_x + adj_x, y + adj_y), word_str, font=font, fill=outline_color)
            
            # Ana renk
            draw.text((current_x, y), word_str, font=font, fill=color)
            
            # X koordinatını ilerlet
            try:
                w_bbox = draw.textbbox((0, 0), word_str, font=font)
                current_x += (w_bbox[2] - w_bbox[0])
            except:
                current_x += 150

        return img
