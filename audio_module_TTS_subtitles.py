import asyncio
from enum import Enum
from syllables import estimate as estimate_syllables



# Used for function annotation. Not required at runtime.
from connection_obs_websocket import OBS_WS_Connection
from audio_module_audio_player import Audio_Manager



async def generate_subtitles(rate:"int", text:"list", obs_ws:"OBS_WS_Connection", audio_player:"Audio_Manager", voice_codes:"Enum"):
    
    try:

        text_words = text.split()

        print(f'DEBUG: Text pieces list is {text_words}')
        print(f'DEBUG: Amount of text pieces is {len(text_words)}')
        
        # Removes voice code if it exists.
        if text_words[0] in [k.value for k in voice_codes]:
            
            text_words.pop(0)

        
        character_limit = 20000


        # Identifies total characters in all of the TTS messages, then splits them into <300 character chunks.
        total_characters = 0
        for word in text_words:
            total_characters += len(word) + 1

        
        if total_characters > character_limit:
            target_subtitle_length = total_characters / (int(total_characters / character_limit) + 1)
        else:
            target_subtitle_length = total_characters


        
        print(f'DEBUG: Generating subtitles.')

        # Continues generating subtitles until there is no more text to display. 
        subtitle = ""

        for word in text_words:
            if len(subtitle) < target_subtitle_length:
                subtitle = subtitle + word + " "

            else:
                await obs_ws.update_text_detail("TTS Subtitles", subtitle)

                sleep_time = estimate_total_syllables(subtitle) / (rate / 40)
                print(f"Waiting for {sleep_time} seconds before changing subtitles again.")
                await asyncio.sleep(sleep_time)

                subtitle = word + " "

        await obs_ws.update_text_detail("TTS Subtitles", subtitle)
            


    except Exception as e:
        print("Subtitles ended early! This is not necessarily an error, sometimes TTS happens faster than expected.")
        print(f"Received exception: \n{e}")



# Estimates the number of syllables in a full subtitle.
def estimate_total_syllables(text:"str") -> int:
    syllable_count = 0
    words = text.split()

    print("DEBUG: Estimating syllables.")

    for word in words:
        syllable_count += estimate_syllables(word)
        print(f"DEBUG: Syllable count is {syllable_count} after estimating syllables in {word}.")

    return syllable_count


            
    # Subtitle Requirements:
    # - If <20 words, show all.
    # - If >20 words, split evenly with min value 10 and max value 20.
    # - Single line cannot exceed 40 characters. Lines capped at 4. Max total characters 160 for multiple words.
    # - If line exceeds 40 characters, remove 1 word and add it to a new line.