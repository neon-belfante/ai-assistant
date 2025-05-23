import speech_recognition as sr

class voiceRecognitionFactory:
    def __init__(self):
        self.register = {
            'whisper (offline) pt-br' : voiceRecognitionWhisperPTBR,
            'whisper (offline)' : voiceRecognitionWhisper,
            'google (online) pt-br': voiceRecognitionGooglePTBR,
            'google (online)': voiceRecognitionGoogle
            }

class voiceRecognitionGoogle:
    '''Online speech recognition'''
    def __init__(self):
        self  = self
        self.recognizer = sr.Recognizer()
        self.voiceCommands = {
            'next' : 'next',
            'back' : 'back',
            'hey listen' : 'hey listen',
            'bye' : 'bye'
        }
        
    def capture_voice_input(self, timeout=None):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, phrase_time_limit=timeout)
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
    
class voiceRecognitionGooglePTBR:
    '''Online speech recognition'''
    def __init__(self):
        self  = self
        self.recognizer = sr.Recognizer()
        self.voiceCommands = {
            'next' : 'próximo',
            'back' : 'volta',
            'hey listen' : 'escuta',
            'bye' : 'tchau'
        }
        
    def capture_voice_input(self, timeout=None):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, phrase_time_limit=timeout)
        return audio

    def convert_voice_to_text(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language='pt-br')
            print("You said: " + text)
        except sr.UnknownValueError:
            text = ""
            print("Sorry, I didn't understand that.")
        except sr.RequestError as e:
            text = ""
            print("Error; {0}".format(e))
        return text
    
class voiceRecognitionWhisperPTBR:
    '''Offline speech recognition'''
    def __init__(self):
        self  = self
        self.recognizer = sr.Recognizer()
        self.voiceCommands = {
            'next' : 'próximo',
            'back' : 'volta',
            'hey listen' : 'escuta',
            'bye' : 'tchau'
        }
        
    def capture_voice_input(self, timeout=None):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, phrase_time_limit=timeout)
        return audio

    def convert_voice_to_text(self, audio):
        try:
            text = self.recognizer.recognize_whisper(audio, language='pt')
            print("You said: " + text)
        except sr.UnknownValueError:
            text = ""
            print("Sorry, I didn't understand that.")
        except sr.RequestError as e:
            text = ""
            print("Error; {0}".format(e))
        return text

class voiceRecognitionWhisper:
    '''Offline speech recognition'''
    def __init__(self):
        self  = self
        self.recognizer = sr.Recognizer()
        self.voiceCommands = {
            'next' : 'next',
            'back' : 'back',
            'hey listen' : 'hey listen',
            'bye' : 'bye'
        }
        
    def capture_voice_input(self, timeout=None):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, phrase_time_limit=timeout)
        return audio

    def convert_voice_to_text(self, audio):
        try:
            text = self.recognizer.recognize_whisper(audio, language='en')
            print("You said: " + text)
        except sr.UnknownValueError:
            text = ""
            print("Sorry, I didn't understand that.")
        except sr.RequestError as e:
            text = ""
            print("Error; {0}".format(e))
        return text

    