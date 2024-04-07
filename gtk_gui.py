import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
import os
from setup import *
# from imageGenerator import imageGenerator
from textGenerator import textGenerator
from ellaAssistant import ella
from voiceGenerator import voiceGeneratorSpeecht5
import datetime
import cairo
import joblib

def createStoryList(complete_story: str):
    return complete_story.split("\n\n")

def openImageFromPath(image_path: str):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
    return pixbuf

class Application(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Assistant")

        self.assistant = ella()
        self.voice = voiceGeneratorSpeecht5()
        self.textGenerator = textGenerator()

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.add(self.main_box)

        self.topMenuContainer = Gtk.Box()
        self.main_box.pack_start(self.topMenuContainer, False, False, 0)

        self.imageContainer = Gtk.Box()
        self.main_box.pack_start(self.imageContainer, False, False, 0)

        self.backAndNextButtonsContainer = Gtk.Grid()
        self.main_box.pack_start(self.backAndNextButtonsContainer, False, False, 0)

        self.textGeneratorResultContainer = Gtk.Box()
        self.main_box.pack_start(self.textGeneratorResultContainer, False, False, 0)

        self.enterTextContainer = Gtk.Grid()
        self.main_box.pack_start(self.enterTextContainer, False, False, 0)

        self.enterText = Gtk.Entry()
        self.enterText.set_width_chars(30)
        self.enterText.set_hexpand(True)
        self.enterTextContainer.attach(self.enterText, 0,0,1,1)

        self.enterButton = Gtk.Button()
        self.enterButton.set_image(Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON))
        self.enterButton.set_tooltip_text("Send Message")
        self.enterButton.connect("clicked", self.actionCallOllama)
        self.enterTextContainer.attach_next_to(self.enterButton,  self.enterText, 1, 10, 5)

        self.addSizeSlider()
        self.addCropSlider()
        self.addSaveMessageHistOption()
        self.addLoadMessageHistOption()
        self.setMenuButton()
        
        self.createUploadButton()

        self.imagePath = self.assistant.imagesPaths[self.assistant.standByEmotion]
        self.imgSize = 100

        
        self.openOriginalImage()

        self.counterStoryParts = 0
        self.counterEnter = 0
        self.interview_history = [{'role':'user', 'content':f'*For context* today is "{datetime.datetime.now().strftime("%Y %B %d, %A, %H:%M %p")}"'}]        
        self.longTermMemory = None
        self.filePathToRead = None

        self.makeWindowTransparent()
        self.setStyling()

    def addLoadMessageHistOption(self):
        self.loadMessageHistButton = Gtk.EventBox()
        self.loadMessageHistButtonIcon =  Gtk.Image.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON)
        self.loadMessageHistButton.add(self.loadMessageHistButtonIcon)
        self.loadMessageHistButton.connect("button_press_event", self.onLoadMessageHistClicked)
        self.loadMessageHistButton.set_tooltip_text("Load message history from file")

    def onLoadMessageHistClicked(self, button, image):
        self.loadMessageHistDialog = Gtk.FileChooserDialog(
            title = "Load message hist dialog", 
            parent = self, 
            action = Gtk.FileChooserAction.OPEN
        )
        self.loadMessageHistDialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.loadMessageHistDialog.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        self.loadMessageHistDialog.set_default_response(Gtk.ResponseType.OK)

        self.filter_gz = Gtk.FileFilter()
        self.filter_gz.set_name("Gzip files (*.gz)")
        self.filter_gz.add_pattern("*.gz")
        self.loadMessageHistDialog.add_filter(self.filter_gz)

        self.loadMessageHistResponse = self.loadMessageHistDialog.run()
        if self.loadMessageHistResponse == Gtk.ResponseType.OK:
            self.loadMessageHistPath = self.loadMessageHistDialog.get_filename()
            self.interview_history = self.interview_history + joblib.load(f"{self.loadMessageHistPath}")
            self.longTermMemory = self.textGenerator.loadLongTermMemory(f"{self.loadMessageHistPath.split('.')[0]}_long_term_memory.txt")
        elif self.loadMessageHistResponse == Gtk.ResponseType.CANCEL:
            print("Messages Hist load cancelled")
        self.loadMessageHistDialog.destroy()   

    def addSaveMessageHistOption(self):
        self.saveMessageHistButton = Gtk.EventBox()
        self.saveMessageHistButtonIcon =  Gtk.Image.new_from_icon_name("document-save-symbolic", Gtk.IconSize.BUTTON)
        self.saveMessageHistButton.add(self.saveMessageHistButtonIcon)
        self.saveMessageHistButton.connect("button_press_event", self.onSaveMessageHistClicked)
        self.saveMessageHistButton.set_tooltip_text("Save current message history")         

    def onSaveMessageHistClicked(self, button, image):
        self.saveMessageHistDialog = Gtk.FileChooserDialog(
            title = "Save message hist dialog", 
            parent = self, 
            action = Gtk.FileChooserAction.SAVE
        )
        self.saveMessageHistDialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.saveMessageHistDialog.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        self.saveMessageHistDialog.set_default_response(Gtk.ResponseType.OK)

        self.filter_gz = Gtk.FileFilter()
        self.filter_gz.set_name("Gzip files (*.gz)")
        self.filter_gz.add_pattern("*.gz")
        self.saveMessageHistDialog.add_filter(self.filter_gz)

        self.saveMessageHistResponse = self.saveMessageHistDialog.run()
        if self.saveMessageHistResponse == Gtk.ResponseType.OK:
            self.saveMessageHistPath = self.saveMessageHistDialog.get_filename()
            joblib.dump(self.interview_history[50:], f"{self.saveMessageHistPath}")
            longTermMemoryPath = f"{self.saveMessageHistPath.split('.')[0]}_long_term_memory.txt"
            longTermMemorySummary = self.textGenerator.callMessageHistSummariser(self.interview_history)
            ltm = open(longTermMemoryPath, "a")
            ltm.write(str(longTermMemorySummary))
            ltm.close()
            self.longTermMemory = self.textGenerator.loadLongTermMemory(longTermMemoryPath)
        elif self.saveMessageHistResponse == Gtk.ResponseType.CANCEL:
            print("Messages Hist save cancelled")
        self.saveMessageHistDialog.destroy()

    def setMenuButton(self):
        self.menu = Gtk.Popover()
        self.menu_button = Gtk.EventBox()
        self.menu_button_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        self.menu_button.add(self.menu_button_icon)
        self.menu_button.connect("button_press_event", self.onMenuButtonClicked)
        self.topMenuContainer.pack_end(self.menu_button, False, False, 0)

        self.menuGrid = Gtk.Grid()
        self.menuGrid.set_row_spacing(1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("zoom-in-symbolic", Gtk.IconSize.BUTTON), 0, 0, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("image-crop-symbolic", Gtk.IconSize.BUTTON), 1, 0, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("media-floppy-symbolic", Gtk.IconSize.BUTTON), 2, 0, 1,1)
        self.menuGrid.attach(self.saveMessageHistButton, 2, 2, 1,20)
        self.menuGrid.attach(self.loadMessageHistButton, 2, 21, 1, 20)
        self.menuGrid.attach(self.imageSizeScale, 0, 1, 1, 200)
        self.menuGrid.attach(self.imageCropScale, 1, 1, 1, 200)
        self.menu.add(self.menuGrid)
        self.menu.set_size_request(100, 200)

    def onMenuButtonClicked(self, button, image):
        self.menu.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def createUploadButton(self):
        self.uploadButton = Gtk.Button()
        self.uploadButtonIcon = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.BUTTON)
        self.uploadButton.set_image(self.uploadButtonIcon)
        self.uploadButton.connect("clicked", self.uploadAction)
        self.uploadButton.set_tooltip_text("Upload image as context for the assistant")
        self.enterTextContainer.attach_next_to(self.uploadButton,  self.enterButton, 1, 1, 1)

    def uploadAction(self, button):
        self.uploadDialog = Gtk.FileChooserDialog(
            title = "Please choose a file", 
            parent = self, 
            action = Gtk.FileChooserAction.OPEN
        )
        self.uploadDialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.uploadDialog.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        self.uploadResponse = self.uploadDialog.run()
        if self.uploadResponse == Gtk.ResponseType.OK:
            self.filePathToRead = self.uploadDialog.get_filename()
        elif self.uploadResponse == Gtk.ResponseType.CANCEL:
            print("File selection cancelled")
        self.uploadDialog.destroy()

    def openOriginalImage(self):
        self.image = Gtk.Image()
        self.updateImage(None)
        self.imageContainer.set_center_widget(self.image)
        self.imageContainer.set_hexpand(True)
        self.imageContainer.set_vexpand(True)
    
    def addSizeSlider(self):
        self.imageSizeScale = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL, -130, -25, 1)
        self.imageSizeScale.set_draw_value(False)
        self.imageSizeScale.set_value(-100)
        self.imageSizeScale.connect("value-changed", self.updateImage)
    
    def addCropSlider(self):
        self.imageCropScale = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL, -100, -25, 1)
        self.imageCropScale.set_draw_value(False)
        self.imageCropScale.set_value(-100)
        self.imageCropScale.connect("value-changed", self.updateImage)

    def updateImage(self, scale):
        self.pixbuf = openImageFromPath(self.imagePath)
        self.updateImageSize()
        self.pixbuf = self.pixbuf.scale_simple(self.desired_width, self.desired_height, 2)
        self.updateImageCrop()
        self.cropped_pixbuf = self.pixbuf.new_subpixbuf(0, 0, self.desired_width, self.cropped_height)
        self.image.set_from_pixbuf(self.cropped_pixbuf)

    def updateImageSize(self):
        self.imgSize = self.imageSizeScale.get_value() * (-1)
        self.desired_width = self.pixbuf.get_width() * (self.imgSize/100)
        self.desired_height = self.pixbuf.get_height() * (self.imgSize/100)
        print(self.imgSize)
    
    def updateImageCrop(self):
        self.imgSize = self.imageCropScale.get_value() * (-1)
        self.cropped_height = self.pixbuf.get_height() * (self.imgSize/100)
        print(self.imgSize)

    def makeWindowTransparent(self):
        self.set_border_width(30)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        self.set_visual(self.visual)
        self.set_app_paintable(True)
        self.connect("draw", self.area_draw)
        self.show_all()
    
    def area_draw(self, widget, cr):
        cr.set_source_rgba(.2, .2, .2, 0.4)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
    
    def setStyling(self):
        self.provider = Gtk.CssProvider()
        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(self.screen, 
                                                   self.provider, 
                                                   Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.css = b'''
#image-border {border-style: inset; border-color: red;}
'''
        self.provider.load_from_data(self.css)
        self.imageContainer.set_name('image-border')

    def createTextResultsBox(self):
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_min_content_height(80)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.textGeneratorResultContainer.pack_start(self.scroll, True, True, 0)

        self.result = Gtk.TextView()
        self.result.set_wrap_mode(Gtk.WrapMode.WORD)
        self.scroll.add(self.result)
        self.show_all()       
    
    def playAudio(self, mp3_list):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        for i, mp3 in enumerate(mp3_list):
            if i == 0:
                pygame.mixer.music.load(mp3)
            else:
                pygame.mixer.music.queue(mp3)
            pygame.mixer.music.play(loops=0)

    def createBackAndNextButtons(self):
        self.backButton = Gtk.Button()
        self.backButton.set_image(Gtk.Image.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON))
        self.backButton.connect("clicked", self.actionBack)
                
        self.nextButton = Gtk.Button()
        self.nextButton.set_image(Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON))
        self.nextButton.connect("clicked", self.actionNext)
        
        self.pagesIndicatorNewText = Gtk.Label(label="")
        
        self.backAndNextButtonsContainer.attach(self.backButton, 0, 0, 1, 1)
        self.backAndNextButtonsContainer.attach(self.pagesIndicatorNewText, 1, 0, 1,1)
        self.backAndNextButtonsContainer.attach(self.nextButton, 2, 0, 1, 1)
        self.backAndNextButtonsContainer.set_halign(Gtk.Align.CENTER)
        self.show_all()

    def actionBack(self, widget):
        if self.counterStoryParts == 0:
            self.counterStoryParts = len(self.story_list) - 1
        else:
            self.counterStoryParts -= 1
        self.imagePath = self.img_list[self.counterStoryParts]
        self.updateImage(None)
        self.result.get_buffer().set_text(self.story_list[self.counterStoryParts])
        self.voiceOutputList = self.voice.generateVoice(self.story_list[self.counterStoryParts])
        self.pagesIndicatorNewText.set_text("{}/{}".format(self.counterStoryParts + 1, len(self.story_list)))
        self.playAudio(self.voiceOutputList)

    def actionNext(self, widget):
        if self.counterStoryParts == len(self.story_list) - 1:
            self.counterStoryParts = 0
        else:
            self.counterStoryParts += 1
        self.imagePath = self.img_list[self.counterStoryParts]
        self.updateImage(None)
        self.result.get_buffer().set_text(self.story_list[self.counterStoryParts])
        self.voiceOutputList = self.voice.generateVoice(self.story_list[self.counterStoryParts])
        self.pagesIndicatorNewText.set_text("{}/{}".format(self.counterStoryParts + 1, len(self.story_list)))
        self.playAudio(self.voiceOutputList)

    def actionCallOllama(self, widget):
        if self.filePathToRead is not None:
            prompt = self.textGenerator.callImageReader(self.enterText.get_text(), self.filePathToRead)
            self.filePathToRead = None
        else:
            prompt = self.enterText.get_text()
        result = self.textGenerator.callOllama(prompt=prompt, message_hist=self.interview_history, model=self.assistant.modelName, db=self.longTermMemory)
        self.story_list = createStoryList(result)
        self.img_list = self.createImageListFromEmotions(self.story_list, self.assistant)
        self.counterStoryParts = 0
        if self.counterEnter == 0:
            self.createTextResultsBox()
            self.createBackAndNextButtons()
        self.pagesIndicatorNewText.set_text("{}/{}".format(self.counterStoryParts + 1, len(self.story_list)))
        self.counterEnter = 1
        self.result.get_buffer().set_text(self.story_list[0])
        self.imagePath = self.img_list[0]
        self.updateImage(None)
        self.voiceOutputList = self.voice.generateVoice(prompt=self.story_list[0])
        self.playAudio(self.voiceOutputList)
    
    def createImageListFromEmotions(self, story_list: list[str], assistantClass):
        img_list = []
        for story_i in story_list:
            emotion_i = self.textGenerator.defineEmotion(story_i, assistantClass.emotionsList)
            image_path = assistantClass.imagesPaths[emotion_i]
            img_list.append(image_path)
        return img_list

def main():
    app = Application()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
