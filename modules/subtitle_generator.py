import os

class ASSSubtitleGenerator:
    @staticmethod
    def create_ass_file(word_timestamps, output_ass_path):
        """
        Ultra Kalite Shorts Altyazısı:
        - Büyük Harf Dönüşümü (UPPERCASE)
        - Ekranın tam ortasında/hafif altında (Alignment 2 / MarginV 750)
        - Kalın 8px Siyah Kontur + Yumuşak Arka Plan Gölgesi
        - Aktif Kelime: Parlak Sarı (#00FFFF / &H0000FFFF&) + Büyük Harf
        - Pasif Kelimeler: Saf Beyaz (#FFFFFF / &H00FFFFFF&)
        """
        
        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,Montserrat,82,&H00FFFFFF,&H0000FFFF,&H00000000,&H90000000,-1,0,0,0,105,105,2,0,1,8,4,2,60,60,750,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        chunk_size = 3
        chunks = [word_timestamps[i:i + chunk_size] for i in range(0, len(word_timestamps), chunk_size)]

        for chunk in chunks:
            if not chunk:
                continue
            
            # Her kelime grubu ekranda konuşulurken sırayla sarı yansın
            for current_word in chunk:
                w_start = ASSSubtitleGenerator._format_time(current_word['start'])
                w_end = ASSSubtitleGenerator._format_time(current_word['end'])
                
                text_parts = []
                for w in chunk:
                    clean_word = w['word'].upper()  # Tüm harfleri BÜYÜK yapıyoruz
                    if w == current_word:
                        # AKTİF KELİME: Parlak Sarı & Kalın Görünüm
                        text_parts.append(f"{{\\c&H0000FFFF&\\b1}}{clean_word}{{\\r}}")
                    else:
                        # PASİF KELİMELER: Saf Beyaz
                        text_parts.append(f"{{\\c&H00FFFFFF&}}{clean_word}")
                
                line_text = " ".join(text_parts)
                events.append(f"Dialogue: 0,{w_start},{w_end},ShortsStyle,,0,0,0,,{line_text}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events))
            
        return output_ass_path

    @staticmethod
    def _format_time(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        msecs = int((seconds % 1) * 100)
        return f"{hrs}:{mins:02d}:{secs:02d}.{msecs:02d}"
