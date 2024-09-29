# import sys
# sys.path.append('/home/neon/bark')

# from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from IPython.display import Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf
import os
from gtts import gTTS
import re
import datetime
import numpy as np

class voiceGeneratorGtts:
    def __init__(self, speaker = None) -> None:
        self.savePath = "example.mp3"
        self.speaker = None

    def updateSpeaker(self, speaker:str):
        pass

    def generateVoice(self, prompt: str):
        print(f"Starting voice generator: {datetime.datetime.now()}")
        prompt_actions_removed = re.sub("\*.*?\*", "", prompt)
        audio = gTTS(text=prompt_actions_removed, lang="en", slow=False)
        audio.save(self.savePath)
        print(f"Ended voice generator: {datetime.datetime.now()}")
        return [self.savePath]

# class voiceGeneratorBark:
#     def __init__(self):
#         self.savePath = 'bark_generation.wav'
#         os.environ["SUNO_OFFLOAD_CPU"] = "True"
#         os.environ["SUNO_USE_SMALL_MODELS"] = "True"
#         preload_models()
        
#     def generateVoice(self, prompt: str):
#         print(f"Starting voice generator: {datetime.datetime.now()}")
#         audio_array = generate_audio(prompt, history_prompt='v2/en_speaker_9')
#         write_wav(self.savePath, SAMPLE_RATE, audio_array)
#         print(f"Ended voice generator: {datetime.datetime.now()}")
#         return [self.savePath]

class voiceGeneratorMeloTTS:
    def __init__(self, speaker, speed = 1) -> None:
        from MeloTTS.melo.api import TTS
        self.speed = speed
        self.model = TTS(language='EN', device='auto')
        self.output_path = 'example.mp3'
        self.speakers = {'EN-US': 0, 
                         'EN-BR': 1, 
                         'EN_INDIA': 2, 
                         'EN-AU': 3, 
                         'EN-Default': 4}
        self.speaker = speaker
        self.speaker_code = self.speakers[self.speaker]
    
    def generateVoice(self, prompt: str):
        start_time = datetime.datetime.now()
        print(f"Starting voice generator: {start_time}")
        prompt_actions_removed = re.sub("\*.*?\*", "", prompt)
        self.model.tts_to_file(prompt_actions_removed, self.speaker_code, self.output_path, self.speed)
        list_outputs = [self.output_path]
        print(f"Ended voice generator: {datetime.datetime.now()}, elapsed time: {datetime.datetime.now() - start_time}")
        return list_outputs

class voiceGeneratorSpeecht5:
    def __init__(self, speaker):
        self.savePath = "example"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(self.device)
        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(self.device)
        self.embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation", trust_remote_code=True)
        self.speaker = speaker
        self.speakers = {
            'awb': 0,     # Scottish male
            'bdl': 1138,  # US male
            'clb': 2271,  # US female
            'jmk': 3403,  # Canadian male
            'ksp': 4535,  # Indian male
            'rms': 5667,  # US male
            'slt': 6799   # US female
        }
        self.speaker_code = self.speakers[self.speaker]
    
    def generateVoice(self, prompt: str):
        start_time = datetime.datetime.now()
        print(f"Starting voice generator: {start_time}")
        # preprocess text
        prompt_actions_removed = re.sub("\*.*?\*", "", prompt)
        inputs = self.processor(text=prompt_actions_removed, return_tensors="pt").to(self.device)
        if self.speaker_code is not None:
            # load xvector containing speaker's voice characteristics from a dataset
            speaker_embeddings = torch.tensor(self.embeddings_dataset[self.speaker_code]["xvector"]).unsqueeze(0).to(self.device)
        else:
            # random vector, meaning a random voice
            speaker_embeddings = torch.randn((1, 512)).to(self.device)
        # generate speech with the models
        if len(inputs['input_ids'][0]) < 600:
            speech = self.model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=self.vocoder)
            sf.write(f"{self.savePath}.mp3", speech.cpu().numpy(), samplerate=16000)
            list_outputs = [f"{self.savePath}.mp3"]
        else:
            temp_list_inputs = inputs['input_ids'][0].numpy()
            list_inputs = []
            list_outputs = []   
            for i in range(0, len(temp_list_inputs), 550):
                list_inputs.append(temp_list_inputs[i:i+550])
            for i, input_i in enumerate(list_inputs):
                speech = self.model.generate_speech(torch.tensor(np.array([input_i])), speaker_embeddings, vocoder=self.vocoder)
                sf.write(f"{self.savePath}{i}.mp3", speech.cpu().numpy(), samplerate=16000)
                list_outputs.append(f"{self.savePath}{i}.mp3")
        print(f"Ended voice generator: {datetime.datetime.now()}, elapsed time: {datetime.datetime.now() - start_time}")
        return list_outputs
        

