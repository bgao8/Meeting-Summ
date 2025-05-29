import speech_recognition as sr
import pyaudio
import pyttsx3
from vosk import Model, KaldiRecognizer
from shared_state import is_recording

r = sr.Recognizer()
# model = Model("vosk-model-en-us-0.22")

continue_recording = False

def start_recording():
    global continue_recording
    continue_recording = True
    # print("Starting recording...")

def end_recording():
    global continue_recording
    continue_recording = False
    # print("Ended recording")

def record_text(mic_index):
    while(is_recording()): 
        # try:
            with sr.Microphone(device_index=mic_index) as source:
                if source.stream is None:
                    raise ValueError("Mic at this index does not exist")
                # r.adjust_for_ambient_noise(source, duration=0.2gv)
                audio = r.listen(source, timeout=100, phrase_time_limit=100)
                transcribed = r.recognize_vosk(audio)

                return transcribed
            
    #     except sr.WaitTimeoutError:
    #         print("No speech detected in time, retrying...")
    #         continue

    #     except sr.RequestError as e:
    #         print(f"Could not request results; {e}")
    #         continue
        
    #     except sr.UnknownValueError as e:
    #         print(f"Unknown error occurred; {e}")
    #         continue
    
    # return

def output_text(text, filename = "displayed_text.txt"):
    with open(filename, 'a') as file:
        file.write(text)
        file.write("\n")
        file.close()

def log_recording(device_index):
    try:
        # print("Starting recording...")
        while(is_recording):
            text = record_text(device_index)

            if text is None:
                continue
            # if "exit" in text.lower():
            #     print("Exiting loop.")
            #     break
            if not is_recording():
                print("Stopped recording.")
                break

            print("Wrote text")
            output_text(text)
            
    except KeyboardInterrupt:
        print("\nManual interruption received. Exiting.")