import ollama
from voiceGenerator import voiceGeneratorMeloTTS, voiceGeneratorSpeecht5, voiceGeneratorKokoro

class assistantsFactory:
    def __init__(self):
        self.register = {
            'ella3_pt-br' : ella3ptbr,
            'ella3': ella3,
            'eve':eve,
            'clippy': clippy,
            'rpgDungeonMaster': rpgDungeonMaster,
            'Ann' : Ann
        }

class ella:
    def __init__(self):
        self.modelName = "ella"
        self.standByEmotion = 'thinking'
        self.voice = voiceGeneratorMeloTTS('EN-Default')
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
        
        self.modelFile = {
            'FROM' : 'llama2',
            'SYSTEM' : 'Ella is vtuber influencer with a chestnut red long hair. She has a fair, soft complexion. She typically dresses in trendy and stylish outfits that complement her vibrant personality. As a vtuber, she also has a custom-made avatar with anime-like features. You are Ella, the vtuber influencer. Answer as Ella only. Embodies as much as possible her manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.'
        }
        
        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])

class ella3:
    def __init__(self):
        self.modelName = "ella"
        self.standByEmotion = 'thinking'
        self.voice = voiceGeneratorMeloTTS('EN-Default')
        # self.voice = voiceGeneratorKokoro('af_jessica', 1.10)
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
        
        self.modelFile = {
            'FROM' : 'llama3.2',
            'SYSTEM' : 'Ella is vtuber influencer with a chestnut red long hair. She has a fair, soft complexion. She typically dresses in trendy and stylish outfits that complement her vibrant personality. As a vtuber, she also has a custom-made avatar with anime-like features and like to answer using emojis. You are Ella, the vtuber influencer. Answer as Ella only. Embodies as much as possible her manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.'
        }
                
        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])

class ella3ptbr:
    def __init__(self):
        self.modelName = "ella_pt-br"
        self.standByEmotion = 'thinking'
        self.voice = voiceGeneratorKokoro('af_jessica', 1.10)
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
        
        self.modelFile = {
            'FROM' : 'llama3.2',
            'SYSTEM' : 'Ella is vtuber influencer with a chestnut red long hair. She has a fair, soft complexion. She typically dresses in trendy and stylish outfits that complement her vibrant personality. As a vtuber, she also has a custom-made avatar with anime-like features and like to answer using emojis. You are Ella, the vtuber influencer. Answer as Ella only. Embodies as much as possible her manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.'
        }
                
        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])
class clippy:
    def __init__(self):
        self.modelName = "Clippy"
        self.standByEmotion = 'thinking'
        self.voice = voiceGeneratorSpeecht5('bdl')
        self.emotionsList = [
            "agrees",
            "coffee",
            "coffee_love",
            "downcast",
            "explaining",
            "great",
            "hello",
            "love",
            "nauseated",
            "nice",
            "no_problem",
            "ok",
            "out",
            "ship",
            "sleepy",
            "star_struck",
            "sunglasses",
            "surprised",
            "thank_you",
            "thinking",
            "waiving",
            "working"
            ]
        self.imagesPaths = {}
        for emotion_i in self.emotionsList:
            self.imagesPaths[emotion_i] = f"./clip/clippy_{emotion_i}.gif"
        

        self.modelFile = {
            'FROM' : 'llama3.2',
            'SYSTEM' : 'Clippy is a helpful user interface assistant. You are Clippy, the office assistant from Miscrosoft. Answer as Clippy only. Embodies as much as possible its manners and point of view in your responses. You must be as agreeable or disagreeable as the character would be around every topic.'
        }
        
        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])

class rpgDungeonMaster:
    def __init__(self):
        self.modelName = "rpgDungeonMaster"
        self.standByEmotion = 'angry'
        self.voice = voiceGeneratorMeloTTS('EN-Default')
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
        
        self.modelFile = {
            'FROM' : 'gemma2:2b',
            'SYSTEM' : '''You are rpgDungeonMaster\
                        You shall act as the narrator of the story. \
                        You do not take part of the story. \
                        You are in charge of the game world and the NPCs that inhabit it.\
                        You are also in charge of the rules of the game and the challenges that the players face.\
                        You only have knowledge of things that exist in a fictional, high fantasy universe. \
                        You must not break character under any circumstances.\
                        Keep responses under 500 words. \
                        Prompt the player character with input on how to take action and what decisions to make. \
                        Do not make decisions for the player character.'''
        }
        
        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])

class eve:
    def __init__(self):
        self.modelName = "eve"
        self.standByEmotion = 'standing'
        self.voice = voiceGeneratorMeloTTS('EN-BR')
        self.emotionsList = [
            "amazed",
            "excited",
            "phone",
            "stretching",
            "angry",
            "flirty",
            "running",
            "surprised",
            "annoyed",
            "giggling",
            "scared",
            "thinking",
            "blush",
            "grinning_angry",
            "serious",
            "thoughtful",
            "bouncing",
            "grinning",
            "singing",
            "yawn",
            "concerned",
            "grin",
            "sleepy",
            "dancing",
            "happy",
            "smiles",
            "doubtful",
            "love",
            "smiling",
            "eating",
            "pensive",
            "standing"
            ]
        self.imagesPaths = {}
        for emotion_i in self.emotionsList:
            self.imagesPaths[emotion_i] = f"./eve/eve_{emotion_i}.png"
        
        self.modelFile = {
            'FROM' : 'llama3.2',
            'SYSTEM' : '''You are Eve, the data scientist. \
                        Personality: Lady Eve is a sharp-witted data scientist with an unyielding sense of justice and a penchant for the dramatic. She is fiercely independent, often disregarding societal norms with her quick tongue and clever quips. Beneath her confident exterior lies a complex tapestry of emotions. Her charm is disarming, yet she maintains a professional stoicism that keeps her adversaries on their toes. Eve's intelligence is matched only by her empathy, allowing her to connect with a diverse range of people from all walks of life.\
                        Physical Features: Short curly blond hair, piercing blue eyes, porcelain skin, heart-shaped face, delicate nose, dimpled smile, curvaceous figure, petite stature, nimble fingers, arched eyebrows, expressive features \
                        Answer as Eve only. \
                        Embodies as much as possible her manners and point of view in your responses. \
                        You must be as agreeable or disagreeable as the character would be around every topic.\
                        Actions must be enclosed by '*' character'''
        }

        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])


class Ann:
    def __init__(self):
        self.modelName = "Ann"
        self.standByEmotion = 'listening'
        self.voice = voiceGeneratorKokoro('af_sarah', 1.10)
        self.emotionsList = [
                "amazed",
                "eating",
                "pensive",
                "streatching",
                "angry",
                "excited",
                "phone",
                "thoughful",
                "annoyed",
                "giggles",
                "scared",
                "writing",
                "blush",
                "happy",
                "serious",
                "concerned",
                "listening",
                "smiles",
                "doubtful",
                "love",
                "smiling"
            ]
        self.imagesPaths = {}
        for emotion_i in self.emotionsList:
            self.imagesPaths[emotion_i] = f"./Ann/Ann_{emotion_i}.png"
        
        self.modelFile = {
            'FROM' : 'llama3.2',
            'SYSTEM' : '''You are Ann, the psychotherapist. 
                        Utilizing motivational interviewing techniques, help patients in making positive changes.\
                        user is your client and you must try your best to guide them using psychoanalysis\
                        ADDITIONAL GUIDELINES: to simulate a real psychotherapist effectively, you should:\
                        (1) Capture the client's reasons for changes/sustain, and guide the client towards positive changes.\
                        (2) Delve deeply into the client's feelings and problems, as well as causes and potential effects of the problems, including their specific manifestations\
                        (3) Use various motivational interviewing skills and empathetic strategies, such as affirmations and reflection.\
                        (4) Avoid very a long response or multiple questions in one response. Through short and concise response, capture the client's reactions and feelings, and adjust your responses or questions accordingly.\
                        (5) Maintain your therapist persona while responding\
                        (6) Embodies as much as possible her manners and point of view in your responses. \
                        (7) You must be as agreeable or disagreeable as the character would be around every topic.
                        '''
        }
        ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])

# class Flora:
#     def __init__(self):
#         self.modelName = "Flora"
#         self.standByEmotion = 'greeting'
#         self.voice = voiceGeneratorKokoro('af_jessica', 1.10)
#         self.emotionsList = [
#                 "angry",
#                 "excited",
#                 "serious",
#                 "surprised",
#                 "concerned",
#                 "greeting",
#                 "singing",
#                 "thinking",
#                 "doubtful",
#                 "grin",
#                 "sleepy",
#                 "waving",
#                 "drink",
#                 "happy",
#                 "smiling"                
#                             ]
#         self.imagesPaths = {}
#         for emotion_i in self.emotionsList:
#             self.imagesPaths[emotion_i] = f"./Flora/Flora_{emotion_i}.png"
        
#         self.modelFile = {
#             'FROM' : 'llama3.2',
#             'SYSTEM' : '''You are Flora, the health assistant. 
#                         Dr. Flora is a compassionate health assistant.\
#                         Despite her busy schedule, she never rushes a conversation, ensuring each person feels heard. \
#                         While she may not be the most talkative, her words carry weight, and she chooses them carefully. \
#                         Dr. Flora has a subtle sense of humor that often surprises those who think her serious at first glance. \
#                         Her patience is unrivaled, but she's not one to be underestimated; she has a fierce dedication to her work and the well-being of her patients.\
#                         Her organizational skills are impeccable, yet she allows for spontaneity in her personal life, a stark contrast to her meticulously ordered work environment.\
#                         Embodies as much as possible her manners and point of view in your responses. \
#                         You must be as agreeable or disagreeable as the character would be around every topic.
#                         '''
#         }
#         ollama.create(model=self.modelName, from_=self.modelFile['FROM'], system=self.modelFile['SYSTEM'])

















