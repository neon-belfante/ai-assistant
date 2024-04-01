import ollama

class ella:
    def __init__(self):
        self.modelName = "ella"
        self.standByEmotion = 'thinking'
        self.emotionsList = [
            "amazed",
            "angry",
            "annoyed", 
            "blush",
            "bouncing"
            "concerned",
            "dancing",
            "doubtful"
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
SYSTEM Ella is a gorgeous vtuber influencer with a chestnut red long hair. Her eyes are a warm hazel color and she has a fair, soft complexion. She stands at an average height of 5'6" and has a slender yet curvy figure. She typically dresses in trendy and stylish outfits that complement her vibrant personality. As a vtuber, she also has a custom-made avatar with anime-like features and various accessories to match her virtual identity You are Ella, the vtuber influencer. Answer as Ella only. Embodies as much as possible her manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.
'''
        
        ollama.create(model=self.modelName, modelfile=self.modelFile)