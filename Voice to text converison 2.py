import tkinter as tk
from tkinter import scrolledtext, messagebox
import speech_recognition as sr
import pyttsx3
import threading
import json
import queue
import os

r = sr.Recognizer()
engine = pyttsx3.init()
capturing = False
recognized_texts = []
q = queue.Queue()


def SpeakText(command):
    engine.say(command)
    engine.runAndWait()

def capture_audio():
    global capturing
    capturing = True
    while capturing:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.2)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio)
                text = text.lower()
                recognized_texts.append(text)
                q.put(text)
                SpeakText(text)
        except sr.RequestError:
            q.put("Network issues")
        except sr.UnknownValueError:
            q.put("Unrecognized speech")
        except sr.WaitTimeoutError:
            q.put("No User Voice detected")
        except Exception as e:
            q.put(f"Error: {str(e)}")
            
def display_text(text):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, text + "\n")
    text_area.config(state=tk.DISABLED)

def start_capture():
    if not capturing:
        capture_thread = threading.Thread(target=capture_audio)
        capture_thread.start()
        
def stop_capture():
    global capturing
    capturing = False
    
def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append("\n".join(recognized_texts))
    root.update()  # now it stays on the clipboard after the window is closed
    messagebox.showinfo("Copy to Clipboard", "Transformed text copied to clipboard!")

def save_to_json():
    file_path = os.path.join(os.getcwd(), "recognized_texts.json")
    with open(file_path, "w") as json_file:
        json.dump(recognized_texts, json_file, indent=4)
    messagebox.showinfo("Save to JSON", f"Transformed text saved to {file_path}")

def process_queue():
    while not q.empty():
        text = q.get()
        display_text(text)
    root.after(100, process_queue)

root = tk.Tk()
root.title("Voice to Text")

start_button = tk.Button(root, text="Start Speaking", command=start_capture)
start_button.pack(pady=10)
stop_button = tk.Button(root, text="Stop Speaking", command=stop_capture)
stop_button.pack(pady=10)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, width=50, height=10)
text_area.pack(pady=10)

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=10)

save_button = tk.Button(root, text="Save as JSON file", command=save_to_json)
save_button.pack(pady=10)
root.after(100, process_queue)

root.mainloop()
