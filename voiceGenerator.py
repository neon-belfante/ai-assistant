from scipy.io.wavfile import write as write_wav
from IPython.display import Audio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import torch
import soundfile as sf
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

class voiceGeneratorMeloTTS:
    def __init__(self, speaker, speed = 1) -> None:
        from MeloTTS.melo.api import TTS
        self.speed = speed
        self.model = TTS(language='EN', device='auto')
        self.output_path = 'example.mp3'
        self.speakers = self.model.hps.data.spk2id
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

class voiceGeneratorKokoro:
    def __init__(self, speaker, speed = 1) -> None:
        from kokoro import KPipeline
        self.speed = speed
        self.savePath = "example"
        self.model = KPipeline(lang_code='p')
        self.speakers = {
            'pf_dora' : 'pf_dora',
            'af_heart' : 'af_heart',
            'jf_alpha' : 'jf_alpha',
            'af_bella' :'af_bella',
            'af_jessica' : 'af_jessica'
        }
        self.speaker = speaker
        self.speaker_code = self.speakers[self.speaker]
    
    def generateVoice(self, prompt: str):
        start_time = datetime.datetime.now()
        print(f"Starting voice generator: {start_time}")
        emoji_pattern = re.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    u"\U00002500-\U00002BEF"  # chinese char
                                    u"\U00002702-\U000027B0"
                                    u"\U000024C2-\U0001F251"
                                    u"\U0001f926-\U0001f937"
                                    u"\U00010000-\U0010ffff"
                                    u"\u2640-\u2642" 
                                    u"\u2600-\u2B55"
                                    u"\u200d"
                                    u"\u23cf"
                                    u"\u23e9"
                                    u"\u231a"
                                    u"\ufe0f"  # dingbats
                                    u"\u3030"
                                    "]+", flags=re.UNICODE)

        prompt = emoji_pattern.sub('', prompt)
        prompt_actions_removed = re.sub("\*.*?\*", "", prompt)
        generator = self.model(
                        prompt_actions_removed, 
                        voice=self.speaker_code,
                        speed=self.speed, 
                        split_pattern=r'\n+'
                    )
        list_outputs = []
        for i, (gs, ps, audio) in enumerate(generator):
            output_path = f'{self.savePath}{i}.mp3'
            sf.write(output_path, audio, 24000)
            list_outputs.append(output_path )
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
        

