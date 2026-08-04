import os
import json
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


class ContentBrain:
    # Rotated mechanically (not left to the model) so consecutive runs
    # don't keep landing on the same angle (e.g. always "door mechanism").
    CAR_SUBCATEGORIES = [
        "üretim süreci ve fabrika sırları",
        "rekor kıran hız/performans özellikleri",
        "gizli/az bilinen mühendislik detayları",
        "en pahalı ve en nadir özel üretim modeller",
        "markanın tarihindeki ilginç/tuhaf olaylar",
        "yarış pisti mirası ve motorsport bağlantısı",
        "ünlü/zengin sahiplerin ilginç hikayeleri",
        "tasarım felsefesi ve dikkat çekici detaylar",
        "güvenlik/dayanıklılık testlerindeki şaşırtıcı sonuçlar",
        "markanın rakiplerinden ayrışan teknolojik yenilikleri",
    ]

    def get_trending_topic(self):
        """
        In a full build, this would scrape Google Trends or Twitter.
        For now, we ask the model to pick a viral niche topic, but we force
        variety by randomly picking a subcategory ourselves first — this
        guarantees the topic angle rotates across runs instead of the model
        drifting back to the same easy answer (e.g. door mechanisms) every time.
        """
        subcategory = random.choice(self.CAR_SUBCATEGORIES)

        prompt = (
            "Bana kısa bir belgesel (Short Documentary) için spesifik, viral "
            "ve DİKKAT ÇEKİCİ 1 konu ver.\n\n"
            "Konu KESİNLİKLE lüks/egzotik otomobil markaları ve modelleri "
            "hakkında olmalı (Rolls Royce, Bugatti, Ferrari, Lamborghini, "
            "BMW, Bentley, Aston Martin, Porsche, McLaren gibi markalardan "
            "biri).\n\n"
            f"Konu ÖZELLİKLE şu açıdan ele alınmalı: **{subcategory}**.\n\n"
            "Konu; sıradan, akademik veya soyut olmamalı. İlk saniyede "
            "izleyicinin durup izlemesini sağlayacak kadar çarpıcı, merak "
            "uyandırıcı ve 'Vay be, bunu bilmiyordum!' dedirtecek nitelikte "
            "olmalı.\n\n"
            "SADECE konu adını Türkçe olarak döndür, başka hiçbir şey yazma."
        )
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        topic = response.choices[0].message.content.strip()
        print(f"🎯 Selected Topic ({subcategory}): {topic}")
        return topic

    def generate_script(self, topic):
        """
        Generates a structured JSON script with visual cues.
        The voiceover text ('text') is in Turkish.
        The visual search terms ('visual_1', 'visual_2') stay in English,
        because Pexels search results are far more reliable in English.
        """
        print(f"📝 Writing script for: {topic}...")
        prompt = f"""
Sen yüksek izlenme oranına sahip bir "Edutainment" YouTube Shorts kanalının
baş senaristisin.
Konu: {topic}

### AMAÇ:
Her cümlede bir "Görsel Geçişi (Visual Switch)" olan bir senaryo oluştur.
İzlenme oranını yüksek tutmak için her sahne için İKİ farklı stok video
kullanacağız.

### 1. SENARYO GEREKSİNİMLERİ (Seslendirme Metni):
- **Dil:** "text" alanındaki tüm metinler **TÜRKÇE** olmalı, doğal ve akıcı bir Türkçe kullan.
- **Uzunluk:** HER sahne metni **15-25 kelime** arasında olmalı. Tek kelimelik
  ya da çok kısa yarım cümlelerden kaçın — her sahne kendi başına doyurucu,
  tam bir düşünce/bilgi içermeli.
- **Bakış Açısı:** Kesinlikle **3. tekil/çoğul şahıs** ("Mühendisler keşfetti...", "Bu model şunu başardı...").
- **Ton:** İlgi çekici, hızlı tempolu, mantıklı. Gereksiz laf kalabalığı yok ama her cümle bilgi dolu olmalı.
- **Yapı:** Toplam 8-9 Sahne.
- **Akış:** Giriş (Hook) -> Bağlam (Context) -> Mekanizma (Nasıl çalışır) -> Sürpriz/Twist -> Kapanış (Outro).

### 2. GÖRSEL GEREKSİNİMLERİ (Çift Görsel):
- HER sahne için İKİ farklı arama terimi ver.
- **ÖNEMLİ:** "visual_1" ve "visual_2" alanları mutlaka **İNGİLİZCE** olmalı
  (Pexels stok video arama motoru İngilizce terimlerde çok daha iyi sonuç veriyor).
  - **visual_1:** Cümlenin *başlangıcıyla* eşleşen İngilizce arama terimi.
  - **visual_2:** Cümlenin *sonuyla* ya da bir tepki/bağlam görseliyle eşleşen İngilizce arama terimi.
- **Kesinlikle Birebir:** Eğer metin "Ekonomi çöktü" ise "sad man" gibi soyut
  bir şey arama. "Stock market red chart" gibi birebir eşleşen bir şey ara.

### ÇIKTI FORMATI (Kesin JSON):
[
    {{
        "id": 1,
        "text": "1995 yılında Yellowstone Parkı'na salınan on dört kurt, bölgedeki nehirlerin akış yönünü bile kalıcı olarak değiştirdi.",
        "visual_1": "wolves running snow aerial",
        "visual_2": "river flowing forest drone",
        "mood": "intriguing"
    }},
    {{
        "id": 2,
        "text": "İlk bakışta imkansız görünen bu değişim, aslında oldukça basit bir biyolojik zincirleme etkiyle açıklanıyor.",
        "visual_1": "person shocked looking at camera",
        "visual_2": "blackboard math equations chalk",
        "mood": "educational"
    }}
]

### ÖNEMLİ
Sadece geçerli JSON döndür.

Hiçbir açıklama yazma.

Markdown kullanma.

JSON'u ```json içine sarma.

Sadece JSON dizisini döndür.
"""

        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        clean_text = (
            response.choices[0].message.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            script = json.loads(clean_text)
        except json.JSONDecodeError as e:
            print("⚠️ JSON parse edilemedi, model çıktısı:")
            print(clean_text)
            raise e

        return script


# --- TESTING THE MODULE ---
if __name__ == "__main__":
    brain = ContentBrain()
    topic = brain.get_trending_topic()
    script = brain.generate_script(topic)

    # Save to file to verify
    with open("script.json", "w") as f:
        json.dump(script, f, indent=4)
        print("✅ Script saved to script.json")
        
