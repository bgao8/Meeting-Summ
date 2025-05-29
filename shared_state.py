# this file connects the continue_recording bool from
# speech_text_onclick to meeting_summarizer, since
# we run the whole thing from widgets, which runs meeting_summarizer,
# which runs speech_text_onclick

continue_recording = False

def set_recording(status):
    global continue_recording
    continue_recording = status

def is_recording():
    return continue_recording