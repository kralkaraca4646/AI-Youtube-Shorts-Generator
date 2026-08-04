import os
import asyncio
import edge_tts
from mutagen.mp3 import MP3
import ffmpeg

class AudioEngine:
    def __init__(self, voice="tr-TR-AhmetNeural"):
        self.voice = voice
        self.output_dir = os.path.join(os.getcwd(), "assets", "audio_clips")
        self.sfx_dir = os.path.join(os.getcwd(), "assets", "sfx")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.sfx_dir, exist_ok=True)

    async def generate_audio(self, text, output_filename, is_first_scene=False, retries=3):
        output_path = os.path.join(self.output_dir, output_filename)

        for attempt in range(retries):
            try:
                communicate = edge_tts.Communicate(text, self.voice, rate="+10%")
                await communicate.save(output_path)

                # --- HOOK SFX MİKSLEME ---
                sfx_path = os.path.join(self.sfx_dir, "hook.mp3")
                if is_first_scene and os.path.exists(sfx_path):
                    mixed_output = os.path.join(self.output_dir, f"sfx_{output_filename}")
                    try:
                        voice_in = ffmpeg.input(output_path)
                        sfx_in = ffmpeg.input(sfx_path).filter('volume', '0.4')

                        mixed = ffmpeg.filter([voice_in, sfx_in], 'amix', inputs=2, duration='first')
                        out = ffmpeg.output(mixed, mixed_output, acodec='libmp3lame')
                        out.run(overwrite_output=True, quiet=True)
                        return mixed_output
                    except Exception as sfx_err:
                        print(f"⚠️ SFX mixing failed, using plain voice: {sfx_err}")
                        return output_path

                return output_path

            except Exception as e:
                print(f"      ⚠️ Audio Error (Attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise e

    def get_audio_duration(self, file_path):
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            print(f"❌ Error reading audio length: {e}")
            return 0.0

    async def process_script(self, scenes):
        print(f"🎙️ Starting Audio Generation for {len(scenes)} scenes...")

        for idx, scene in enumerate(scenes):
            scene_id = scene['id']
            text = scene['text']
            filename = f"voice_{scene_id}.mp3"
            is_first = (idx == 0)

            try:
                file_path = await self.generate_audio(text, filename, is_first_scene=is_first)
                duration = self.get_audio_duration(file_path)

                scene['audio_path'] = file_path
                scene['duration'] = duration

                print(f"   ✅ Scene {scene_id}: {duration:.2f}s generated.")
                await asyncio.sleep(1)

            except Exception as e:
                print(f"   ❌ Skipping Scene {scene_id} due to audio error.")
                continue

        return scenes
        
