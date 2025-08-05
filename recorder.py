import speech_recognition as sr
import queue

class Recorder:
    def __init__(self):
        self.r = sr.Recognizer()
        self.recording = False  # Bool condition to determine live text status
        self.queue = queue.Queue()
    # model = Model("vosk-model-en-us-0.22")

    # Getter
    def is_recording(self):
        return self.recording

    # =============== Setters ===============
    def start_recording(self):
        self.recording = True

    def end_recording(self):
        self.recording = False

    # =============== Helpers for log_recording ===============
    # Mic_index selected with dropdown, mic control and SR implementation
    def record_text(self, mic_index):
        if not self.recording:
            return None
        
        try:
            with sr.Microphone(device_index=mic_index) as source:
                # r.adjust_for_ambient_noise(source, duration=0.2gv)
                audio = self.r.listen(source, timeout=5, phrase_time_limit=10)
                transcribed = self.r.recognize_vosk(audio) # use Vosk, built into SR

                return transcribed
                
        except sr.WaitTimeoutError:
            return

        except sr.RequestError as e:
            return
            
        except sr.UnknownValueError as e:
            return

    # Writes into the file
    def write_text(self, text, filename='displayed_text.txt'):
        with open(filename, 'a') as file:
            file.write(text)
            file.write("\n")
            file.close()

    # ============================================================
    # Directly called by MeetingSummarizer instance
    def log_recording(self, device_index):
        try:
            # print("Starting recording...")
            while(self.is_recording()):
                text = self.record_text(device_index)

                # =============== MAKE THIS DO SOMETHING ===============
                if text is None:     # make this flag mean something
                    continue
                # if "exit" in text.lower():
                #     print("Exiting loop.")
                #     break
                if not (self.is_recording()):
                    print("Stopped recording.")
                    break
                # ======================================================

                # print("Wrote text")
                self.write_text(text)
                self.queue.put(text)    # push text into queue
                
        except KeyboardInterrupt:
            print("\nManual interruption received. Exiting.")