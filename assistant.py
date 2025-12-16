# assistant.py
# Core assistant logic for MS VOISE AI
# Dependencies: speech_recognition, pyttsx3, wikipedia, webbrowser, openai (optional)

import os
import time
import webbrowser
import platform
from datetime import datetime

import speech_recognition as sr
import pyttsx3
import wikipedia

try:
    import openai
except Exception:
    openai = None


class Assistant:
    def __init__(self, name="ms voise"):
        self.name = name.lower()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # Initialize TTS
        self.tts = pyttsx3.init()
        # (Optional) configure voice/rate
        try:
            voices = self.tts.getProperty("voices")
            # choose a voice if available (0 default)
            if voices:
                self.tts.setProperty("voice", voices[0].id)
        except Exception:
            pass
        self.tts.setProperty("rate", 150)
        # OpenAI setup if key present in env
        api_key = os.environ.get("OPENAI_API_KEY") or None
        if api_key and openai:
            openai.api_key = api_key
            self.openai_enabled = True
        else:
            self.openai_enabled = False

    def speak(self, text):
        print("MS VOISE AI:", text)
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception as e:
            print("TTS error:", e)

    def listen(self, timeout=6, phrase_time_limit=8):
        """Listen from microphone and return recognized text or None."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return None
        try:
            text = self.recognizer.recognize_google(audio, language="hi-IN")
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print("Speech API error:", e)
            return None

    def is_wake_word(self, text):
        if not text:
            return False
        text = text.lower()
        # Accept few variants
        wake_variants = [self.name, "ms voice", "ms voice ai", "ms voice assistant", "ms voise"]
        return any(w in text for w in wake_variants)

    def handle_command(self, command):
        if not command:
            self.speak("Maine kuch nahin suna. Dobara boliye.")
            return

        print("Command received:", command)

        # Simple patterns
        if "time" in command or "samay" in command or "kitne baje" in command:
            now = datetime.now().strftime("%I:%M %p")
            self.speak(f"Abka samay hai {now}")
            return

        if "wikipedia" in command or "who is" in command or "kya hai" in command:
            # find search term
            try:
                # Remove word 'wikipedia' if present
                term = command.replace("wikipedia", "").replace("kya hai", "").strip()
                if not term:
                    self.speak("Wikipedia ke liye kya search karun?")
                    term = self.listen(timeout=5, phrase_time_limit=6)
                    if not term:
                        self.speak("Thik hai.")
                        return
                summary = wikipedia.summary(term, sentences=2, auto_suggest=True)
                self.speak(summary)
            except Exception as e:
                print("Wiki error:", e)
                self.speak("Maaf kijiye, Wikipedia se jawab nahin mila.")
            return

        if "search" in command or "google" in command or "kholo" in command:
            # open a web search
            # try to extract query
            query = command
            # remove trigger words
            for w in ["google", "search", "kholo", "dhoondo", "open"]:
                query = query.replace(w, "")
            query = query.strip()
            if not query:
                self.speak("Kya search karun?")
                query = self.listen(timeout=5, phrase_time_limit=6)
            if query:
                url = "https://www.google.com/search?q=" + webbrowser.quote(query)
                webbrowser.open(url)
                self.speak(f"Search kar raha hoon: {query}")
            else:
                self.speak("Theek hai, kuch nahin.")
            return

        if "open youtube" in command or "youtube" in command:
            webbrowser.open("https://www.youtube.com")
            self.speak("YouTube khol raha hoon.")
            return

        if "joke" in command or "hans" in command:
            jokes = [
                "Ek aadmi doctor ke paas gaya. Bola: Doctor saab, main bhoolne laga hoon. Doctor: Kab se? Aadmi: Kab se kya?",
                "Teacher: Agar tumhare paas 10 aam hain aur tum 2 kha lo to kitne bachenge? Student: Sir, aam ke daane bach jayenge."
            ]
            import random
            self.speak(random.choice(jokes))
            return

        if "exit" in command or "quit" in command or "stop" in command or "band" in command:
            self.speak("Theek hai. Main band ho raha hoon. Namaste!")
            raise SystemExit

        # Fallback: use OpenAI if enabled
        if self.openai_enabled:
            reply = self.ask_openai(command)
            if reply:
                self.speak(reply)
                return

        # Default simple reply
        self.speak("Maaf kijiye, main woh nahi samajh paaya. Aap dubara kah sakte hain ya mujhe try karne ke liye 'Wikipedia' ya 'search' bolen.")

    def ask_openai(self, prompt):
        if not openai:
            return None
        try:
            # Use chat completion (gpt-3.5-turbo)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are MS VOISE AI, a helpful Hindi/English assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7,
            )
            text = response["choices"][0]["message"]["content"].strip()
            return text
        except Exception as e:
            print("OpenAI error:", e)
            return None