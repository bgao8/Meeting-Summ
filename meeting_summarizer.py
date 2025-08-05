import os
import openai
from dotenv import load_dotenv
from recorder import Recorder

# Load from the correct env file
# print("Retrieving key")
load_dotenv('key.env')

# Get API key from environment variable instead of hardcoding
# GitHub will not allow sharing if API key is not hidden
openai.api_key = os.getenv('OPENAI_API_KEY')

# goal is to create a MeetingSummarizer object that can call 
class MeetingSummarizer:
    def __init__(self):
        # create an instance of Recorder, now the MeetingSummarizer instance has 
        # its own recorder called self.recorder
        self.recorder = Recorder()
        self.poll_timer = None

    # =============== Widget calls relayed to recorder instance ===============
    def start_recording(self, mic_index):
        self.recorder.start_recording()
        self.recorder.log_recording(mic_index)

    def end_recording(self):
        self.recorder.end_recording()
        if self.poll_timer:
            self.poll_timer.cancel()
            self.poll_timer = None

    # ============================================================

    # transcript_file gets passed in from display_summary()
    def read_file(self, transcript_file='displayed_text.txt'):
        try:
            with open(transcript_file, 'r') as file:
                transcript = file.read()

            print(f"Reading transcript.")
            return transcript

        except IOError as e:
            print(f"Failed to open file {e}")
            raise

        except Exception as e:
            raise

    def ask(self, question, transcript_file='displayed_text.txt'):
        if not question:
            return

        transcript = self.read_file(transcript_file)

        prompt = f'Here is a meeting prompt: {transcript}. Answer this question based on the meeting: {question}'

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[ {"role":"system", "content":"Answer the question at the end given the rest of the transcript."}, 
                {"role":"user", "content":prompt}
                ]
            )

            ai_response = response.choices[0].message.content
            print("Question answered.")
            return ai_response
        
        except Exception as e:
            print(f'Error: {e}')
            raise

    # calls OpenAI API
    def summary_call(self, prompt):
        try:
            print("Loading summary...")
            response = openai.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    { "role":"system", "content":
                    "You are an AI assistant that analyzes meeting transcripts"
                    " and extracts key information. Summarize this text to a"
                    " student who has no background information about it."
                    " Summary, Key Points, Decisions. The header for each section"
                    " should just be the 'summary', 'key points', and 'decisions' "
                    " with regular text formatting in all caps. "
                    "Note that these transcripts are created by a speech-text app and"
                    " may have inaccuracies."},
                    
                    # User message. What are we asking as the user?
                    {"role":"user", "content":prompt}
                ]
            )

            ai_response = response.choices[0].message.content
            print("Summary completed.")
            return ai_response

        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            raise

    def summarize_meeting(self, transcript_file):
        # file io
        prompt = self.read_file(transcript_file)    
        response = self.summary_call(prompt)
        # splitting response into sections
        sections = response.split('\n\n')
        # print('raw sections = ', sections)

        results = {
            'summary': '',
            'key_points': [],
            'decisions': [],
            'other':[],
        }

        # ============================== Display stuff ==============================
        def parse_section(sect):
            # removing the spaces before and after, joins the lines from the stripped first line
            # (only if more than one line)
            lines = sect.strip().split('\n')
            if (len(lines) > 1): 
                return '\n'.join(lines[1:]).strip()
            else: 
                return ''

        for section in sections:
            if not section: 
                continue

            upper_line = section.strip().split('\n')[0].strip().upper()
            section = parse_section(section)

            if section.startswith('SUMMARY'):
                results['SUMMARY'] = section.replace('SUMMARY', '').strip()
            # summary section always starts with summary or 1. 
            
            if upper_line == 'SUMMARY':
                results['summary'] = section
                continue
            # key point section always start with **key
            if upper_line == 'KEY POINTS':
                results['key_points'].append(section)
                continue
            
            if upper_line == 'DECISIONS':
                results['decisions'].append(section)
                continue

            else:
                results['other'].append(section)

        return results
    
    # Formatting answer
    def display_summary(self, transcript_file='displayed_text.txt'):
        transcript = self.read_file(transcript_file)
        results = self.summarize_meeting(transcript_file)
        # print("raw result = ", results)

        if results:
            print("\n" + "=" * 50)
            print("MEETING SUMMARY")
            print("=" * 50)

            print("\nSUMMARY:")
            print(results['summary'])

            print("\nKEY POINTS:")
            for point in results['key_points']:
                print(f"{point}")

            print("\nDECISIONS:")
            for decision in results['decisions']:
                print(f"{decision}")

    def display_transcript(self, transcript_file='displayed_text.txt'):
        transcript = self.read_file(transcript_file)
        print(transcript)
