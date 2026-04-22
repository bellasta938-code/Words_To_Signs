from fastapi import FastAPI
from fastapi.responses import FileResponse
import numpy as np
import cv2
import os
from PIL import Image
from googletrans import Translator

app = FastAPI()

# ================== إعدادات ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
op_dest = os.path.join(BASE_DIR, "filtered_data")
alpha_dest = os.path.join(BASE_DIR, "alphabet")

translator = Translator()

# تحميل الكلمات
dirListing = os.listdir(op_dest)
editFiles = [item for item in dirListing if item.endswith(".webp")]
file_map = {i: i.replace(".webp", "").split() for i in editFiles}


# ================== وظائف ==================

def smart_translate(word):
    for file, group in file_map.items():
        if word.lower() in [w.lower() for w in group]:
            return word, False
    try:
        translated = translator.translate(word, dest='en').text
        return translated, True
    except:
        return word, True


def remove_text(img):
    cv2.rectangle(img, (210, 20), (360, 110), (240, 240, 240), -1)
    return img


def generate_gif(text):
    all_frames = []
    words = text.strip().split()

    for word in words:
        found = False
        exact_file = ""

        for file, group in file_map.items():
            if word.lower() in [w.lower() for w in group]:
                found = True
                exact_file = file
                break

        if found:
            im = Image.open(os.path.join(op_dest, exact_file))

            for f in range(im.n_frames):
                im.seek(f)
                im.save("tmp.png")

                img = cv2.imread("tmp.png")
                img = cv2.resize(img, (380, 260))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                img = remove_text(img)
                all_frames.append(Image.fromarray(img))

        else:
            translated, _ = smart_translate(word)

            for ch in translated.lower():
                gif_path = os.path.join(alpha_dest, f"{ch}_small.gif")
                if not os.path.exists(gif_path):
                    continue

                im = Image.open(gif_path)

                for f in range(im.n_frames):
                    im.seek(f)
                    im.save("tmp.png")

                    img = cv2.imread("tmp.png")
                    img = cv2.resize(img, (380, 260))
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                    all_frames.append(Image.fromarray(img))

        blank = Image.new('RGB', (380, 260), color=(240, 240, 240))
        all_frames.append(blank)

    output_path = "output.gif"

    all_frames[0].save(
        output_path,
        save_all=True,
        append_images=all_frames[1:],
        duration=180,
        loop=0
    )

    return output_path


# ================== API ==================

@app.get("/")
def home():
    return {"message": "Sign Language API is running 🚀"}


@app.get("/convert")
def convert(text: str):
    gif_path = generate_gif(text)
    return FileResponse(gif_path, media_type="image/gif")