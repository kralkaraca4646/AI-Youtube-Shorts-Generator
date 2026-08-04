import os

class ASSSubtitleGenerator:
    @staticmethod
    def create_ass_file(word_timestamps, output_ass_path):
        """
        word_timestamps: [{'word': 'Bugün', 'start': 0.1, 'end': 0.4}, ...]
        CapCut stili: Kelimeler ekranda bloklar halinde görünür, 
        konuşulan kelime anlık olarak Sarı (#00FFFF / &H0000FFFF&) yanar!
        """
        
        # ASS Header (Stil ayarları)
        # PrimaryColour: Beyaz (&H00FFFFFF), SecondaryColour: Sarı (&H0000FFFF)
        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,72,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,960,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        
        # Kelimeleri 3'erli gruplar halinde ekrana getirelim
        chunk_size = 3
        chunks = [word_timestamps[i:i + chunk_size] for i in range(0, len(word_timestamps), chunk_size)]

        for chunk in chunks:
            if not chunk:
                continue
            
            line_start = chunk[0]['start']
            line_end = chunk[-1]['end']
            
            # Zamanları ASS formatına dönüştür (0:00:00.00)
            start_str = ASSSubtitleGenerator._format_time(line_start)
            end_str = ASSSubtitleGenerator._format_time(line_end)
            
            # Her kelime için vurgu efekti
            for current_word in chunk:
                w_start = ASSSubtitleGenerator._format_time(current_word['start'])
                w_end = ASSSubtitleGenerator._format_time(current_word['end'])
                
                text_parts = []
                for w in chunk:
                    if w == current_word:
                        # Aktif kelimeyi SARI yap (\c&H0000FFFF&)
                        text_parts.append(f"{{\\c&H0000FFFF&}}{w['word']}{{\\r}}")
                    else:
                        # Diğer kelimeler BEYAZ
                        text_parts.append(w['word'])
                
                line_text = " ".join(text_parts)
                events.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{line_text}")

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
