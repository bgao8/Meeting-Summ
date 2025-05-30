import os
import openai
from dotenv import load_dotenv
import speech_text_onclick
import shared_state

load_dotenv()

# Load from the correct env file
# print("Retrieving key")
load_dotenv("key.env")

# Get API key from environment variable instead of hardcoding
# openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

openai.api_key = os.getenv("OPENAI_API_KEY")

def start_recording(mic_index):
    shared_state.set_recording(True)
    speech_text_onclick.log_recording(mic_index)

def end_recording():
    # print("Stopping...")
    shared_state.set_recording(False)
    
# transcript_file gets passed in from display_summary()
def read_file(transcript_file):
    try:
        with open('displayed_text.txt', 'r') as file:
            transcript = file.read()

        print(f"Reading transcript.")
        return transcript

    except IOError as e:
        print(f"Failed to open file {e}")
        raise

    except Exception as e:
        raise

# system_prompt = "You are an AI assistant that analyzes meeting transcripts"
# " and extracts key information. Summarize this text to a"
# " student who has no background information about it."
# " Summary, Key Points, Decisions. The header for each section"
# " should just be the 'summary', 'key points', and 'decisions' "
# " with regular text formatting in all caps. "
# "Note that these transcripts are created by a speech-text app and"
# " may have inaccuracies."

def summary_call(prompt):
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

def summarize_meeting(transcript_file):
    # file io
    prompt = read_file(transcript_file)    
    
    response = summary_call(prompt)
    # splitting response into sections
    sections = response.split('\n\n')
    # print('raw sections = ', sections)

    results = {
        'summary': '',
        'key_points': [],
        'decisions': [],
        'other':[],
    }

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
    
# display, effectively main
def display_summary():
    transcript_file = "displayed_text.txt"
    
    if not os.path.exists(transcript_file):
        print(f"File not found: {transcript_file}")
        return  # Exit if file doesn't exist

    results = summarize_meeting(transcript_file)
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
