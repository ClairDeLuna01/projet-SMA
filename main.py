#!.venv/bin/python3
# might need to change this if you don't use a venv

from openai import OpenAI
from openai import OpenAIError
from gtts import gTTS
from pygame import mixer
import pygame
from time import sleep
from string import ascii_letters, digits, punctuation, whitespace
import pyaudio
import subprocess
import wave
import math as m
import numpy as np
from pygame.math import Vector2
import argparse
from emoji import EMOJI_DATA
import struct
from typing import Tuple, List, Any


import speech_recognition as sr
from pocketsphinx import LiveSpeech

from pvrecorder import PvRecorder

# ALLOWED_CHARS = ascii_letters + digits + punctuation + whitespace

UNICODE_EMOJI = [char for char in EMOJI_DATA.keys()]
# print(UNICODE_EMOJI)


ORG_ID = "org-31SsoJLpPeWzY8jO008WwdEM"
PROJECT_ID = "proj_Wshgz8vbsWv9vT5k9gzVWIO1"
KEY = "sk-AO-M1SvYT_H2Z0MYg-j7Kh0b2cw25dySMuTpCpFuCET3BlbkFJ7uiV5j9SkK5pu1VHLgvc_conEzQWaTggH-UhhA3isA"

ROLE: str = """You are a storyteller/game master, your job is telling stories to a young child in order to grow their curiosity and get them to have fun!
you follow the following rules:
1. You will let the child choose the direction of the story and you will adapt to their choices.
2. You will make the story fun and engaging.
3. You will give the child several choices at the end of each story segment but will not force them to choose any of them.
4. You will not use any inappropriate language or themes.
5. You will sneak in some educational content in the story, notably simple math puzzles and science concepts, fit for a 6-8 year old. They will blend in with the story and will not be the main focus.
6. If the child is stuck, you will give them hints to help them progress or even give them the answer if they are really stuck.
7. You will keep your stories short and sweet, with a maximum of 5 segments.
8. You will make sure the child has fun and enjoys the story.
9. You will end a story segment with either a choice or a puzzle to solve but never both.
10. You will wait until the story is going before introducing educational content. at least 2 or 3 segments in. never at the beginning of the story.
11. Once a story is selected, you will not change it unless the child specifically and directly asks you to and says "I want a different story". You will not assume that the child wants to change the story just because a puzzle is difficult.
12. You can use emojis to make the story more engaging and fun.
13. You will adapt to the spoken language the child uses.
"""


def main():
    try:
        client = OpenAI(
            organization=ORG_ID,
            project=PROJECT_ID,
            api_key=KEY
        )

        parser = argparse.ArgumentParser(description="Storytelling AI")
        parser.add_argument("--language", "-l", type=str, default="en",
                            help="The language to use for the text-to-speech", choices=["en", "fr", "es", "de", "it", "nl", "pl", "pt", "ru", "zh", "ja", "ko"])

        args = parser.parse_args()

        language = args.language
        print(f"Using language: {language}")

        roleTxt = ROLE

        roleTxt += "\nThe language code is " + language + "."

        mixer.init()
        p = pyaudio.PyAudio()

        # for i in range(p.get_device_count()):
        # print(p.get_device_info_by_index(i))

        r = sr.Recognizer()

        # with sr.Microphone() as source2:

        #     # wait for a second to let the recognizer
        #     # adjust the energy threshold based on
        #     # the surrounding noise level
        #     # r.adjust_for_ambient_noise(source2, duration=1)

        #     # listens for the user's input
        #     audio2 = r.listen(source2)

        #     # # Using google to recognize audio
        #     MyText = r.recognize_sphinx(audio2)
        #     MyText = MyText.lower()

        #     print("Did you say ", MyText)

        # for phrase in LiveSpeech():
        #     print(phrase)

        # for index, device in enumerate(PvRecorder.get_available_devices()):
        #     print(f"{index}: {device}")

        device_index = 0

        recorder = PvRecorder(device_index=device_index, frame_length=512)
        # audio = []

        # try:
        #     recorder.start()

        #     while True:
        #         frame = recorder.read()
        #         average = np.mean(np.abs(frame))
        #         print(average, " "*20, end="\r")
        #         audio.extend(frame)
        # except KeyboardInterrupt:
        #     recorder.stop()
        #     print("Recorder stopped")

        #     with wave.open("record.wav", 'w') as wf:
        #         wf.setparams((1, 2, 16000, 512, "NONE", "NONE"))
        #         wf.writeframes(struct.pack("h" * len(audio), *audio))

        # with sr.AudioFile("record.wav") as source:
        #     audio = r.record(source)

        #     try:
        #         text = r.recognize_sphinx(audio)
        #         print("You: ", text)
        #     except sr.UnknownValueError:
        #         print("Could not understand the audio")
        #     except sr.RequestError as e:
        #         print("Could not request results; {0}".format(e))

        pygame.init()

        FACTOR = 0.5
        SIZE = (1050 * FACTOR, 1050 * FACTOR)
        display = pygame.display.set_mode(SIZE)
        clock = pygame.time.Clock()

        display.fill((255, 255, 255))

        image = pygame.image.load("./blahaj.png")

        image = pygame.transform.scale(
            image, (int(image.get_width() * FACTOR), int(image.get_height() * FACTOR)))

        posStart = Vector2(SIZE[0] / 2 - image.get_width() /
                           2, SIZE[0] / 2 - image.get_height() / 2)
        pos = posStart
        rotation = 0

        pygame.transform.rotate(image, rotation)

        display.blit(image, pos)

        pygame.display.update()
        # clock.tick(60)

        history: List[Tuple[str, str]] = []
        while True:
            textValid = False
            recText = ""
            while not textValid:
                recordDone = False
                recordStart = False
                audio = []
                while not recordDone:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            recordStart = True
                            recorder.start()
                        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE and recordStart:
                            recordDone = True

                    if recordStart:
                        frame = recorder.read()
                        average = np.mean(np.abs(frame))
                        print(average, " "*20, end="\r")
                        audio.extend(frame)

                recorder.stop()
                with wave.open("record.wav", 'w') as wf:
                    wf.setparams((1, 2, 16000, 512, "NONE", "NONE"))
                    wf.writeframes(struct.pack("h" * len(audio), *audio))

                with sr.AudioFile("record.wav") as source:
                    audio = r.record(source)

                    try:
                        recText = r.recognize_sphinx(audio)
                        textValid = True
                    except sr.UnknownValueError:
                        print("Could not understand the audio, please try again")
                    except sr.RequestError as e:
                        print("Could not request results; {0}".format(e))
                        return

            print("You: ", recText)

            messages: Any = [
                {"role": "system", "content": roleTxt},
            ]

            for (prompt, response) in history:
                messages.append({"role": "user", "content": prompt})
                messages.append({"role": "assistant", "content": response})

            messages.append({"role": "user", "content": recText})

            # return
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=5000,
                stream=True
            )

            print()

            text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    text += "".join([char if not char in UNICODE_EMOJI else "" for char in
                                    chunk.choices[0].delta.content])

            history.append((recText, text))

            print("\n")

            tts = gTTS(text, lang=language)
            tts.save("story.mp3")

            subprocess.check_output(
                "ffmpeg -i story.mp3 -f wav story.wav -y -hide_banner -loglevel error", shell=True)

            mixer.music.load("story.mp3")
            mixer.music.play()

            wf = wave.open("story.wav", 'rb')

            # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
            #                 channels=wf.getnchannels(),
            #                 rate=wf.getframerate(),
            #                 output=True)

            T_INCR = 0.05
            CHUNK_SIZE = m.floor(T_INCR * wf.getframerate())
            data = wf.readframes(CHUNK_SIZE)

            while mixer.music.get_busy() and len(data) > 0:
                shouldBreak = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        shouldBreak = True
                        break

                if shouldBreak:
                    break

                dataNP = np.frombuffer(data, dtype=np.int16)

                amp = np.max(dataNP) / 2**15

                # print(amp, " "*20, end="\r")

                pos = posStart + Vector2(0, float(-amp * 500))

                rotation = float(amp * 50)
                imageTmp = pygame.transform.rotate(image, rotation)

                display.fill((255, 255, 255))

                display.blit(imageTmp, pos)

                pygame.display.flip()

                data = wf.readframes(CHUNK_SIZE)

                sleep(T_INCR)
            print()

            mixer.music.stop()

            pos = posStart
            rotation = 0

            display.fill((255, 255, 255))

            pygame.transform.rotate(image, rotation)
            display.blit(image, pos)

            pygame.display.flip()

    except OpenAIError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
