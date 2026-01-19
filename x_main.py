from command import detect_task_from_speech
from vision import VisionStream
from PA_Communication import rotate
import argostranslate.translate
import time
import sounddevice as sd
import numpy as np
import whisper

model = whisper.load_model("small")

def record_audio(duration=3, fs=16000, device=1):
    print("\n🎙 Speak now...")
    audio = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
        dtype='float32',
        device=device
    )
    sd.wait()
    print("✔ Audio captured!")
    return np.squeeze(audio)

def get_speech_command(device_id=1):
    audio = record_audio(device=device_id)
    result = model.transcribe(audio, fp16=False)

    text = result["text"].strip()
    detected_lang = result.get("language", "en") 

    print(f"🗣 Detected language: {detected_lang}")
    print(f"🗣 You said: {text}")

    if detected_lang == "id":
        translated = argostranslate.translate.translate(text, "id", "en")
        print(f"🇬🇧 Translated to English: {translated}")
        return translated
    return text

vs = VisionStream()
vs.start()

print("Camera running...")

LEFT_THRESH = 300
RIGHT_THRESH = 360
SLEEP_AFTER_ROTATE = 0.1
MAX_ATTEMPTS = 24

current_rotation_degree = 90

while True:
    input("Do you wanna start now? Press ENTER to begin... ")
    user_input = get_speech_command(device_id=1)

    task = detect_task_from_speech(user_input)
    target_object = task[0]
    command = task[1]

    if command == "search":
        found = vs.get_objects(target_object)
        if found:
            print(f"\n--- {target_object.upper()} FOUND ---")

            obj = found[0]
            x1, y1, x2, y2 = obj["bbox"]
            centre_x = (x1 + x2) / 2
            print(f"Initial centre_x = {centre_x}")

            attempts = 0
            while attempts < MAX_ATTEMPTS:

                if centre_x < LEFT_THRESH:
                    print(f"centre_x {centre_x:.1f} < {LEFT_THRESH}, rotating LEFT (2)")
                    current_rotation_degree += 2
                    rotate(2)

                elif centre_x > RIGHT_THRESH:
                    print(f"centre_x {centre_x:.1f} > {RIGHT_THRESH}, rotating RIGHT (-2)")
                    current_rotation_degree -= 2
                    rotate(-2)

                else:
                    print(f"Centered! centre_x = {centre_x:.1f}")
                    break

                time.sleep(SLEEP_AFTER_ROTATE)

                latest = vs.get_objects(target_object)
                if not latest:
                    print("WARNING: Object lost! Stopping.")
                    break

                obj = latest[0]
                x1, y1, x2, y2 = obj["bbox"]
                centre_x = (x1 + x2) / 2
                print(f"After attempt {attempts+1}, centre_x = {centre_x:.1f}")

                attempts += 1
                print(current_rotation_degree)

            else:
                print(f"WARNING: Max attempts ({MAX_ATTEMPTS}) reached.")
        else:
            print(f"\n--- No object detected: {target_object} ---")
    else: 
        print(current_rotation_degree)
        print(f"---ROTATING {90 - current_rotation_degree} degrees!---")
        rotate((90 - current_rotation_degree))
        current_rotation_degree += (90 - current_rotation_degree)