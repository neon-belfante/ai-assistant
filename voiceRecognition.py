import speech_recognition as sr

class voiceRecognition:
    def __init__(self):
        self  = self
        self.recognizer = sr.Recognizer()
        
    def capture_voice_input(self, timeout=None):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, timeout=timeout)
        return audio

    def convert_voice_to_text(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
            print("You said: " + text)
        except sr.UnknownValueError:
            text = ""
            print("Sorry, I didn't understand that.")
        except sr.RequestError as e:
            text = ""
            print("Error; {0}".format(e))
        return text

    # def process_voice_command(text):
    #     if "hello" in text.lower():
    #         print("Hello! How can I help you?")
    #     elif "goodbye" in text.lower():
    #         print("Goodbye! Have a great day!")
    #         return True
    #     else:
    #         print("I didn't understand that command. Please try again.")
    #     return False

    # def main(self):
    #     end_program = False
    #     while not end_program:
    #         audio = self.capture_voice_input()
    #         text = self.convert_voice_to_text(audio)
    #         end_program = self.process_voice_command(text)