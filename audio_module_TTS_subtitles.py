import asyncio
from enum import Enum



# Used for function annotation. Not required at runtime.
from connection_obs_websocket import OBS_WS_Connection
from audio_module_audio_player import Audio_Manager



async def generate_subtitles(self, text:"list", obs_ws:"OBS_WS_Connection", audio_player:"Audio_Manager", voice_codes:"Enum"):
        print(f'DEBUG: TTS partlist is {self._TTS_parts}')

        text_pieces = text.split()

        print(f'DEBUG: Text pieces list is {text_pieces}')
        print(f'DEBUG: Length of text pieces is {len(text_pieces)}')
        
        # Removes voice code if it exists.
        if text_pieces[0] in [k.value for k in voice_codes]:
            
            text_pieces.pop(0)

        while len(text_pieces) > 0 and audio_player.tts_channel_busy_status(): # Condition to continue generating subtitles. TTS_channel is only supposed to be local to the audio manager but don't worry about it ok
            subtitle = ""

            line_limit = 5
            line_character_limit = 30

            print(f'DEBUG: Reached subtitle generation time.')

            ## Identifies target character amount per message.
            total_character_length = 0

            for w in text_pieces:
                total_character_length += len(w)
            
            subtitle_parts = (total_character_length / (line_limit * line_character_limit)) + 1

            target_subtitle_length = total_character_length / subtitle_parts

            if target_subtitle_length < line_character_limit:
                target_subtitle_length = line_character_limit


            # Builds actual subtitle contents.
            while len(text_pieces) > 0:
                
                print(f'DEBUG: Current length of subtitle is {len(subtitle)}. \nCurrent length of text pieces list is {len(text_pieces)}')

                print(f'First text piece is {text_pieces[0]} and its length is {len(text_pieces[0])}')

                # Subtitle complete check.
                if subtitle >= target_subtitle_length:
                    # Identify syllable number, calculate wait time based on syllable count and TTS rate, then asyncio.sleep() for the appropriate time before the next subtitle is needed.
                    # Set subtitle to "" afterwards before continuing through loop.

                    print(f'DEBUG: Generated subtitle is \"{subtitle}\"')


                # Check type A: Subtitle string is incomplete but not empty.
                if subtitle != "":
                    
                    # Check A1: Next word exceeds line character limit when added to current line.
                    if len(text_pieces[0]) + subtitle.split("\n")[-1] > (line_character_limit * line_limit):

                        # Check A1a: Next word combined with existing text exceeds total character limit for all lines.
                        # Result: Subtitle is complete.
                        if len(text_pieces[0]) > (line_limit - len(subtitle.split("\n"))) * line_character_limit:
                            # Identify syllable number, calculate wait time based on syllable count and TTS rate, then asyncio.sleep() for the appropriate time before the next subtitle is needed.
                            # Set subtitle to "" afterwards before continuing through loop.

                            print(f'DEBUG: Generated subtitle is \"{subtitle}\"')
                        
                        
                        # Check A1b: Next word exceeds line character limit alone.
                        # Result: Word is placed on following line and split into pieces.
                        elif len(text_pieces[0]) > line_character_limit:
                            long_word = text_pieces.pop(0)

                            for i in range(int(len(long_word) / (line_character_limit-1)) + 1):
                                long_word = long_word[:(i * (line_character_limit-1))] + "-\n" + long_word[(i * (line_character_limit-1)):]
                            subtitle = subtitle + "\n" + long_word
                            continue

                        # Result:
                        else:
                            subtitle = subtitle + "\n" + text_pieces.pop(0)


                    # Final Result: Word is added normally.
                    else:
                        subtitle = subtitle + text_pieces.pop(0)
                        continue


                # Check type B: Subtitle string is empty.
                else:

                    # Check B1: Single word exceeds the number of characters in 4 lines.
                    # Result: The subtitle is made up of the one word, using as many lines as needed.
                    # COMPLETE SUBTITLE.
                    if len(text_pieces[0]) > (line_character_limit * line_limit):

                        subtitle = text_pieces.pop(0)

                        for i in range(int(len(subtitle) / (line_character_limit-1)) + 1):
                            subtitle = subtitle[:(i * (line_character_limit-1))] + "-\n" + subtitle[(i * (line_character_limit-1)):]
                        continue

                    # Check B2: Single word exceeds the number of characters in 1 line.
                    # Result: The word is split into multiple lines, subtitle is not complete.
                    elif len(text_pieces[0]) > line_character_limit:

                        long_word = text_pieces.pop(0)

                        for i in range(int(len(long_word) / (line_character_limit-1)) + 1):
                            long_word = long_word[:(i * (line_character_limit-1))] + "-\n" + long_word[(i * (line_character_limit-1)):]
                        subtitle = long_word
                        continue

                    # Final Result: The next word is added to the subtitle line.
                    else:
                        subtitle = text_pieces.pop(0)
                        continue


            # Identify syllable number, calculate wait time based on syllable count and TTS rate, then asyncio.sleep() for the appropriate time before the next TTS part.

            print(f'DEBUG: Generated subtitle is \"{subtitle}\"')

            
    # Subtitle Requirements:
    # - If <20 words, show all.
    # - If >20 words, split evenly with min value 10 and max value 20.
    # - Single line cannot exceed 40 characters. Lines capped at 4. Max total characters 160 for multiple words.
    # - If line exceeds 40 characters, remove 1 word and add it to a new line.