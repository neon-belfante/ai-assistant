from setup import *
from imageGenerator import imageGenerator
from textGenerator import textGenerator
from ellaAssistant import ella
from voiceGenerator import *

def createStoryList(complete_story: str):
	return complete_story.split("\n\n")

# def createImageListForImageGenerator(story_list: list[str]):
# 	img_list = []
# 	for story_i in story_list:
# 		if len(story_i) > 100:
# 			summarised_text = textGenerator.summariseText(story_i)
# 			story_i = summarised_text
# 		images = imageGenerator(story_i) 
# 		image_i = images.callImageGenerator()
# 		img_list.append(ImageTk.PhotoImage(image_i))
# 	return img_list

def openImageFromPath(image_path: str):
	image_i = PIL.Image.open(image_path)
	return ImageTk.PhotoImage(image_i)

def createImageListFromEmotions(story_list: list[str], assistantClass):
	img_list = []
	for story_i in story_list:
		emotion_i = textGenerator.defineEmotion(story_i, assistantClass.emotionsList) 
		img_list.append(openImageFromPath(assistantClass.imagesPaths[emotion_i]))
	return img_list

class Application:
	def __init__(self, master=None):
		self.assistant = ella()
		self.voice = voiceGeneratorSpeecht5()

		self.imageContainer = Frame(master)
		self.imageContainer.pack()

		self.textGeneratorResultContainer = Frame(master)
		self.textGeneratorResultContainer.pack()

		self.backAndNextButtonsContainer = Frame(master)
		self.backAndNextButtonsContainer.pack()
		
		self.fonte = ("Arial", "10")
		self.enterTextContainer = Frame(master)
		self.enterTextContainer.pack()
		
		self.enterButtonContainer = Frame(master)
		self.enterButtonContainer.pack()		
				
		self.enterTextLabel = Label(self.enterTextContainer, text = "Enter Text", font=self.fonte)
		self.enterTextLabel.pack(side=LEFT)
		
		self.enterText = Entry(self.enterTextContainer)
		self.enterText["width"]=30
		self.enterText["font"]=self.fonte
		self.enterText.pack(side=LEFT)
		
		self.enterButton = Button(self.enterButtonContainer)
		self.enterButton["text"]="Enter"
		self.enterButton["font"]=self.fonte
		self.enterButton["width"]=10
		self.enterButton["command"] = self.actionCallOllama
		self.enterButton.pack()
		
		self.image = Label(self.imageContainer)
		self.initial_img = openImageFromPath(self.assistant.imagesPaths[self.assistant.standByEmotion])
		self.image.pack()
		self.image["image"] = self.initial_img

		self.v = Scrollbar(self.textGeneratorResultContainer, orient='vertical')
		self.v.pack(side=RIGHT, fill='y')
		
		self.result = Text(self.textGeneratorResultContainer, 
					 wrap=WORD, 
					 yscrollcommand=self.v.set,
					 height=5)
		self.result["font"]=("calibri", "11")
		self.v.config(command=self.result.yview)
		self.result.pack()
		
		self.counterStoryParts = 0
		self.counterEnter = 0
		self.interview_history=[]
	
	def playAudio(self, mp3):
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
		pygame.mixer.music.load(mp3)
		pygame.mixer.music.play(loops=0)
		
	def createBackAndNextButtons(self):
		self.backButton = Button(self.backAndNextButtonsContainer)
		self.backButton["text"]="Back"
		self.backButton["font"]=self.fonte
		self.backButton["width"]=10
		self.backButton["command"] = self.actionBack
		self.backButton.pack(side=LEFT)
		
		self.nextButton = Button(self.backAndNextButtonsContainer)
		self.nextButton["text"]="Next"
		self.nextButton["font"]=self.fonte
		self.nextButton["width"]=10
		self.nextButton["command"] = self.actionNext
		self.nextButton.pack(side=RIGHT)
		
		self.pagesIndicatorNewText=StringVar()
		self.pagesIndicator = Label(self.backAndNextButtonsContainer, textvariable=self.pagesIndicatorNewText)
		self.pagesIndicator["font"] = self.fonte
		self.pagesIndicator.pack(side=LEFT)
	
	def actionBack(self):
		if self.counterStoryParts == 0:
			self.counterStoryParts = len(self.story_list)-1
		else:
			self.counterStoryParts = self.counterStoryParts - 1
		self.image["image"] = self.img_list[self.counterStoryParts]
		self.result.delete('1.0', END)
		self.result.insert(INSERT, self.story_list[self.counterStoryParts])
		self.voice.generateVoice(self.story_list[self.counterStoryParts])
		self.pagesIndicatorNewText.set("{} / {}".format(self.counterStoryParts+1, len(self.story_list)))
		self.playAudio(self.voice.savePath)
		
	
	def actionNext(self):
		if self.counterStoryParts == len(self.story_list)-1:
			self.counterStoryParts = 0
		else:
			self.counterStoryParts = self.counterStoryParts + 1
		self.image["image"] = self.img_list[self.counterStoryParts]
		self.result.delete('1.0', END)
		self.result.insert(INSERT, self.story_list[self.counterStoryParts])
		self.voice.generateVoice(self.story_list[self.counterStoryParts])
		self.pagesIndicatorNewText.set("{} / {}".format(self.counterStoryParts+1, len(self.story_list)))
		self.playAudio(self.voice.savePath)
		
		
	def actionCallOllama(self):
		result = textGenerator.callOllama(self.enterText.get(), self.interview_history, model=self.assistant.modelName)
		self.story_list = createStoryList(result)
		self.img_list = createImageListFromEmotions(self.story_list, self.assistant)
		self.counterStoryParts = 0
		if self.counterEnter == 0:
			self.createBackAndNextButtons()
		self.pagesIndicatorNewText.set("{} / {}".format(self.counterStoryParts+1, len(self.story_list)))
		self.counterEnter = 1
		self.result.delete('1.0', END)
		self.result.insert(INSERT, self.story_list[0])
		self.image["image"] = self.img_list[0]
		self.voice.generateVoice(prompt=self.story_list[0])
		self.playAudio(self.voice.savePath)
		
		
root = Tk()
root.geometry("370x800")
Application(root)
root.mainloop()
