import os
import random
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, vfx
from modules.subtitle_generator import MoviePySubtitleGenerator

class Composer:
    def __init__(self):
        self.temp_dir = os.path.join(os.getcwd(), "assets", "temp")
        self.final_dir = os.path.join(os.getcwd(), "assets", "final")

        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        self.transitions = ['fade']

    def _ensure_min_duration(self, clip, min_duration):
        """
        Kaynak video, ihtiyacımız olan süreden kısaysa MoviePy'nin vfx.loop
        ile baştan tekrar oynatarak süreyi doldurur. Bunu yapmazsak
        set_duration() son kareyi dondurup videoyu 'takılı' gösterir.
        """
        if clip.duration < min_duration:
            clip = clip.fx(vfx.loop, duration=min_duration)
        return clip

    def process_scene(self, scene, video_pair):
        scene_id = scene['id']
        audio_path = scene['audio_path']
        total_duration = scene['duration']
        word_timestamps = scene.get('word_timestamps', [])
        output_path = os.path.join(self.temp_dir, f"scene_{scene_id}.mp4")

        print(f"   🔤 Scene {scene_id}: {len(word_timestamps)} word_timestamps received.")

        try:
            print(f"   ⚙️ Processing Scene {scene_id} with MoviePy...")
            path_a, path_b = video_pair

            # Videoları yükle ve dikey formata (1080x1920) ayarla
            clip_a = VideoFileClip(path_a).resize(height=1920)
            if clip_a.w > 1080:
                x_center = clip_a.w / 2
                clip_a = clip_a.crop(x1=x_center - 540, x2=x_center + 540, y1=0, y2=1920)

            clip_b = VideoFileClip(path_b).resize(height=1920)
            if clip_b.w > 1080:
                x_center = clip_b.w / 2
                clip_b = clip_b.crop(x1=x_center - 540, x2=x_center + 540, y1=0, y2=1920)

            # A/B Split: Yarısı ilk video, yarısı ikinci video
            half_dur = total_duration / 2
            b_dur = half_dur + 0.5

            # 🔧 FIX: Kaynak video kısaysa donmak yerine loop ile doldur
            clip_a = self._ensure_min_duration(clip_a, half_dur)
            clip_b = self._ensure_min_duration(clip_b, b_dur)

            sub_a = clip_a.subclip(0, half_dur)
            sub_b = clip_b.subclip(0, b_dur)

            video_clips = concatenate_videoclips([sub_a, sub_b], method="compose")
            video_clips = video_clips.set_duration(total_duration)

            # Ses dosyasını ekle
            audio_clip = AudioFileClip(audio_path)
            video_clips = video_clips.set_audio(audio_clip)

            # --- MOVIEPY ALTYAZI KATMANLARI (SUBTITLES) ---
            subtitle_clips = [video_clips]

            if word_timestamps:
                chunk_size = 3
                chunks = [word_timestamps[i:i + chunk_size] for i in range(0, len(word_timestamps), chunk_size)]

                for chunk in chunks:
                    for i, active_w in enumerate(chunk):
                        start_t = active_w['start']
                        end_t = active_w['end']

                        if end_t <= start_t:
                            end_t = start_t + 0.2

                        img = MoviePySubtitleGenerator.create_text_clip_image(chunk, i)

                        txt_clip = (ImageClip(np.array(img))
                                    .set_start(start_t)
                                    .set_end(end_t)
                                    .set_duration(end_t - start_t))

                        subtitle_clips.append(txt_clip)
            else:
                print(f"   ⚠️ Scene {scene_id}: word_timestamps boş, altyazı eklenmeyecek.")

            # Tüm katmanları birleştir
            final_scene = CompositeVideoClip(subtitle_clips)

            # Sahneyi renderla
            final_scene.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                logger=None
            )

            # Belleği temizle
            clip_a.close()
            clip_b.close()
            audio_clip.close()
            final_scene.close()

            return output_path

        except Exception as e:
            print(f"❌ MoviePy Render Fail Scene {scene_id}: {e}")
            return None

    def render_all_scenes(self, scenes, video_pairs):
        rendered_paths = []
        for i, scene in enumerate(scenes):
            current_pair = video_pairs[i]
            if current_pair is None:
                continue
            output_path = self.process_scene(scene, current_pair)
            if output_path:
                rendered_paths.append(output_path)
        return rendered_paths

    def concatenate_with_transitions(self, video_paths, output_filename="final_short.mp4"):
        print("🎬 Stitching final video with MoviePy...")
        output_path = os.path.join(self.final_dir, output_filename)

        if not video_paths:
            return None

        try:
            clips = [VideoFileClip(p) for p in video_paths]
            final_video = concatenate_videoclips(clips, method="compose")

            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                logger=None
            )

            for c in clips:
                c.close()
            final_video.close()

            print(f"✅ FINAL VIDEO SAVED: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ MoviePy Stitching Error: {e}")
            return None
