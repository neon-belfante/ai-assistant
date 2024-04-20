import ollama

class assistantsFactory:
    def __init__(self):
        self.register = {
            'ella': ella,
            'ellaAssistant': ellaAssistant
        }

class ella:
    def __init__(self):
        self.modelName = "ella"
        self.standByEmotion = 'thinking'
        self.speaker = "slt"
        self.emotionsList = [
            "amazed",
            "angry",
            "annoyed", 
            "blush",
            "bouncing",
            "concerned",
            "dancing",
            "doubtful",
            "eating",
            "excited",
            "flirty",
            "giggles",
            "grin",
            "grinning",
            "grinning_angry",
            "happy",
            "love",
            "pensive",
            "phone",
            "punching",
            "running",
            "scared",
            "serious",
            "singing",
            "sleepy",
            "smiling",
            "smiles",
            "stretching",
            "surprised",
            "thinking",
            "thoughful",
            "walking",
            "writing",
            "yawn"
            ]
        self.imagesPaths = {}
        for emotion_i in self.emotionsList:
            self.imagesPaths[emotion_i] = f"./ella/ella_{emotion_i}.png"
        
        self.modelFile = '''
FROM llama2
SYSTEM Ella is vtuber influencer with a chestnut red long hair. She has a fair, soft complexion. She typically dresses in trendy and stylish outfits that complement her vibrant personality. As a vtuber, she also has a custom-made avatar with anime-like features. You are Ella, the vtuber influencer. Answer as Ella only. Embodies as much as possible her manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.
'''
        
        ollama.create(model=self.modelName, modelfile=self.modelFile)

class ellaAssistant:
    def __init__(self):
        self.modelName = "ellaAssistant"
        self.standByEmotion = 'writing'
        self.speaker = "clb"
        self.emotionsList = [
            "amazed",
            "angry",
            "annoyed", 
            "blush",
            "bouncing",
            "concerned",
            "dancing",
            "doubtful",
            "eating",
            "excited",
            "flirty",
            "giggles",
            "grin",
            "grinning",
            "grinning_angry",
            "happy",
            "love",
            "pensive",
            "phone",
            "punching",
            "running",
            "scared",
            "serious",
            "singing",
            "sleepy",
            "smiling",
            "smiles",
            "stretching",
            "surprised",
            "thinking",
            "thoughful",
            "walking",
            "writing",
            "yawn"
            ]
        self.imagesPaths = {}
        for emotion_i in self.emotionsList:
            self.imagesPaths[emotion_i] = f"./ella/ella_{emotion_i}.png"
        
        self.modelFile = '''
FROM llama2
SYSTEM Ella is a helpful assistant with a chestnut red long hair. She has a fair, soft complexion. She has a vibrant personality. You are Ella, the assistant. Answer as Ella only. Embodies as much as possible her manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.
'''
        
        ollama.create(model=self.modelName, modelfile=self.modelFile)