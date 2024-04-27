import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk
import os
from setup import *
# from imageGenerator import imageGenerator
from textGenerator import textGenerator
from ellaAssistant import *
from voiceGenerator import voiceGeneratorSpeecht5
from voiceRecognition import voiceRecognition
import datetime
import cairo
import joblib
import threading

def createStoryList(complete_story: str):
    return complete_story.split("\n\n")

def openImageFromPath(image_path: str):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
    return pixbuf

class Application(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Assistant")

        self.assistantFactory = assistantsFactory()
        self.defaultAssistant = "ella"
        self.voice = voiceGeneratorSpeecht5()
        self.textGenerator = textGenerator()
        self.voiceRecognition = voiceRecognition()

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
        self.addVoiceToggleOption()
        self.addBackgroundVoiceRecognitionToggleOption()
        self.addAssistantComboBox()
        self.setMenuButton()
        
        self.createVoiceRecognitionButton()
        self.createUploadButton()

        self.imgSize = 100

        self.openOriginalImage()
        self.updateAssistant(self.defaultAssistant)

        self.counterStoryParts = 0
        self.counterEnter = 0
        self.interview_history_max_length = 4
        self.makeWindowTransparent()
        self.setStyling()
    
    def updateAssistant(self, assistant_name):
        self.assistant = self.assistantFactory.register[assistant_name]()
        self.imagePath = self.assistant.imagesPaths[self.assistant.standByEmotion]
        self.interview_history = [{'role':'user', 'content':f'*For context* today is "{datetime.datetime.now().strftime("%Y %B %d, %A, %H:%M %p")}"'}]
        self.isFirstTimeWritingToLongTermMemory = 0
        self.longTermMemoryPath = None
        self.longTermMemory = None
        self.filePathToRead = None
        self.updateImage(None)
        self.voice.updateSpeaker(self.assistant.speaker)

    def addLoadMessageHistOption(self):
        self.loadMessageHistButton = Gtk.EventBox()
        self.loadMessageHistButtonIcon =  Gtk.Image.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON)
        self.loadMessageHistButton.add(self.loadMessageHistButtonIcon)
        self.loadMessageHistButton.connect("button_press_event", self.onLoadMessageHistClicked)
        self.loadMessageHistButton.set_tooltip_text("Load message history from file")
    
    def onLoadMessageHistClicked(self, button, image):
        def manageFileChooserDialog():
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
            elif self.loadMessageHistResponse == Gtk.ResponseType.CANCEL:
                print("Messages Hist load cancelled")
            self.loadMessageHistDialog.destroy()
        
        def loadMemoryAction():
            interview_history = joblib.load(f"{self.loadMessageHistPath}") + self.interview_history
            longTermMemoryPathNew = f"{self.loadMessageHistPath.split('.')[0]}_long_term_memory.txt"
            try:
                longTermMemory = self.textGenerator.loadLongTermMemory(longTermMemoryPathNew)
            except:
                longTermMemory = None
                print("No Longer Term Memory provided")
            if longTermMemory is not None:
                longTermMemoryPath = longTermMemoryPathNew
            else:
                longTermMemoryPath = self.longTermMemoryPath
            result_dict = {'interview_history': interview_history,
                           'longTermMemory': longTermMemory,
                           'longTermMemoryPath': longTermMemoryPath}
            GLib.idle_add(lambda: updateMemoryVariables(result_dict))
        
        def updateMemoryVariables(result_dict):
            self.interview_history = result_dict['interview_history']
            self.longTermMemory = result_dict['longTermMemory']
            self.longTermMemoryPath = result_dict['longTermMemoryPath']
            self.loadMessageHistButton.set_sensitive(True)
            self.saveMessageHistButton.set_sensitive(True)
            self.restoreButtonIcon(self.enterButton)
            if self.counterEnter != 0:
                self.nextButton.set_sensitive(True)
                self.backButton.set_sensitive(True)
        
        manageFileChooserDialog()
        if self.counterEnter != 0:
            self.nextButton.set_sensitive(False)
            self.backButton.set_sensitive(False)
        self.loadMessageHistButton.set_sensitive(False)
        self.saveMessageHistButton.set_sensitive(False)
        self.addSpinnerToButton(self.enterButton)
        threading.Thread(target=loadMemoryAction).start()

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
            joblib.dump(self.interview_history, f"{self.saveMessageHistPath}")
            if self.longTermMemoryPath is not None:
                longTermMemoryPathNew = f"{self.saveMessageHistPath.split('.')[0]}_long_term_memory.txt"
                if longTermMemoryPathNew != self.longTermMemoryPath:
                    with open(self.longTermMemoryPath,'r') as originalMemoryFile, open(longTermMemoryPathNew,'a') as targetMemoryFile:
                        for line in originalMemoryFile:
                            targetMemoryFile.write(line)
                    self.longTermMemoryPath = longTermMemoryPathNew
        elif self.saveMessageHistResponse == Gtk.ResponseType.CANCEL:
            print("Messages Hist save cancelled")
        self.saveMessageHistDialog.destroy()

    def addVoiceToggleOption(self):
        self.voiceSwitchButton = Gtk.Switch()
        self.voiceSwitchButton.connect("notify::active", self.onVoiceButtonToggled)
        self.voiceSwitchButton.set_active(True)
        self.voiceSwitchButton.set_tooltip_text("Turn on/off assistant speech generation")
        self.voiceOptionOn = True

    def addBackgroundVoiceRecognitionToggleOption(self):
        self.backgroundVoiceSwitchButton = Gtk.Switch()
        self.backgroundVoiceSwitchButton.connect("notify::active", self.onBackgroundVoiceRecognitionButtonToggled)
        self.backgroundVoiceSwitchButton.set_active(False)
        self.backgroundVoiceSwitchButton.set_tooltip_text("Turn on/off background voice recognition \nWhen On try say 'Hey listen' and wait for the Beep")
        self.BackgroundVoiceRecognitionOption = False
    
    def disableToggle(self, toggle):
        self.toggleOriginalPosition = toggle.get_active()
        toggle.set_active(False)
        toggle.set_sensitive(False)
    
    def reenableToggle(self, toggle):
        toggle.set_active(self.toggleOriginalPosition)
        toggle.set_sensitive(True)
        
    def onBackgroundVoiceRecognitionButtonToggled(self, switch, gparam):
        if switch.get_active():
            self.BackgroundVoiceRecognitionOption = True
            self.createBackgroundVoiceRecognition()
            self.voiceRecognitionButton.set_sensitive(False)
        else:
            self.BackgroundVoiceRecognitionOption = False
            self.voiceRecognitionButton.set_sensitive(True)
    
    def onVoiceButtonToggled(self, switch, gparam):
        if switch.get_active():
            self.voiceOptionOn = True
        else:
            self.voiceOptionOn = False

    def setSpinner(self):
        self.spinner = Gtk.Spinner()
        self.topMenuContainer.pack_start(self.spinner, False, False, 0)
    
    def addAssistantComboBox(self):
        self.assistantComboBox = Gtk.ComboBoxText()
        self.assistantList = list(self.assistantFactory.register.keys())
        for assistant_i in self.assistantList:
            self.assistantComboBox.append_text(assistant_i)
        self.assistantComboBox.connect("changed", self.onNewAssistantChosen)
        self.assistantComboBox.set_tooltip_text("Choose assistant")
    
    def onNewAssistantChosen(self, assistantComboBox):
        new_assistant = assistantComboBox.get_active_text()
        if new_assistant is not None:
            self.updateAssistant(new_assistant)

    def setMenuButton(self):
        self.menu = Gtk.Popover()
        self.menu_button = Gtk.EventBox()
        self.menu_button_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        self.menu_button.add(self.menu_button_icon)
        self.menu_button.connect("button_press_event", self.onMenuButtonClicked)
        self.topMenuContainer.pack_end(self.menu_button, False, False, 0)

        self.menuGrid = Gtk.Grid()
        self.menuGrid.set_row_spacing(1)
        self.menuGrid.set_column_spacing(1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("zoom-in-symbolic", Gtk.IconSize.BUTTON), 0, 0, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("image-crop-symbolic", Gtk.IconSize.BUTTON), 0, 1, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("audio-volume-medium", Gtk.IconSize.BUTTON), 0, 2, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("microphone-sensitivity-high", Gtk.IconSize.BUTTON), 0, 3, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("media-floppy-symbolic", Gtk.IconSize.BUTTON), 0, 4, 1,1)
        self.menuGrid.attach(Gtk.Image.new_from_icon_name("avatar-default", Gtk.IconSize.BUTTON), 0, 5, 1,1)
        self.menuGrid.attach(self.imageSizeScale, 1, 0, 170, 1)
        self.menuGrid.attach(self.imageCropScale, 1, 1, 170, 1)
        self.menuGrid.attach(self.voiceSwitchButton, 10, 2, 10, 1)
        self.menuGrid.attach(self.backgroundVoiceSwitchButton, 10, 3, 10, 1)        
        self.menuGrid.attach(self.saveMessageHistButton, 10, 4, 1, 1)
        self.menuGrid.attach(self.loadMessageHistButton, 12, 4, 5, 1)
        self.menuGrid.attach(self.assistantComboBox, 10, 5, 50, 1)
        
        self.menu.add(self.menuGrid)
        self.menu.set_size_request(200, 100)

    def onMenuButtonClicked(self, button, image):
        self.menu.set_relative_to(button)
        self.menu.show_all()
        self.menu.popup()

    def createBackgroundVoiceRecognition(self):
        def getText():
            while self.BackgroundVoiceRecognitionOption:
                captureAudio = self.voiceRecognition.capture_voice_input()
                capturedAudioText = self.voiceRecognition.convert_voice_to_text(captureAudio)
                process_voice_command(capturedAudioText)
            if "hey listen" in capturedAudioText.lower():
                print("other listening")
                GLib.idle_add(lambda: self.voiceRecognitionAction(None))
                    
        def process_voice_command(text):
            if "hey listen" in text.lower():
                print("Generating Response...")
                self.BackgroundVoiceRecognitionOption = False
            else:
                print("I didn't understand that command. Please try again.")
                    
        threading.Thread(target=getText).start() 
            

    def createVoiceRecognitionButton(self):
        self.voiceRecognitionButton = Gtk.Button()
        self.voiceRecognitionButtonIcon = Gtk.Image.new_from_icon_name("microphone-sensitivity-high", Gtk.IconSize.BUTTON)
        self.voiceRecognitionButton.set_image(self.voiceRecognitionButtonIcon)
        self.voiceRecognitionButton.connect("clicked", self.voiceRecognitionAction)
        self.voiceRecognitionButton.set_tooltip_text("Voice message the assistant")
        self.enterTextContainer.attach_next_to(self.voiceRecognitionButton,  self.enterButton, 1, 1, 1)
    
    def voiceRecognitionAction(self, button):
        def getText():
            GLib.idle_add(lambda: self.play_activation_sound())
            captureAudio = self.voiceRecognition.capture_voice_input()
            self.capturedAudioText = self.voiceRecognition.convert_voice_to_text(captureAudio)
            GLib.idle_add(lambda: self.play_activation_sound())
            GLib.idle_add(lambda: updateGui())
            GLib.idle_add(lambda: self.actionCallOllama(None))

        def updateGui():
            self.enterText.set_text(self.capturedAudioText)
            self.restoreButtonIcon(self.voiceRecognitionButton)
        
        self.addSpinnerToButton(self.voiceRecognitionButton)
        if self.counterEnter != 0:
            self.nextButton.set_sensitive(False)
            self.backButton.set_sensitive(False)
        self.loadMessageHistButton.set_sensitive(False)
        self.saveMessageHistButton.set_sensitive(False)
        self.enterButton.set_sensitive(False)
        threading.Thread(target=getText).start()
    
    def play_activation_sound(self):
        Gdk.beep()

    def createUploadButton(self):
        self.uploadButton = Gtk.Button()
        self.uploadButtonIcon = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.BUTTON)
        self.uploadButton.set_image(self.uploadButtonIcon)
        self.uploadButton.connect("clicked", self.uploadAction)
        self.uploadButton.set_tooltip_text("Upload image as context for the assistant")
        self.enterTextContainer.attach_next_to(self.uploadButton,  self.voiceRecognitionButton, 1, 1, 1)

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
        self.imageContainer.set_center_widget(self.image)
        self.imageContainer.set_hexpand(True)
        self.imageContainer.set_vexpand(True)
    
    def addSizeSlider(self):
        self.imageSizeScale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 25, 130, 1)
        self.imageSizeScale.set_draw_value(False)
        self.imageSizeScale.set_value(100)
        self.imageSizeScale.connect("value-changed", self.updateImage)
    
    def addCropSlider(self):
        self.imageCropScale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -100, -25, 1)
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
        self.imgSize = self.imageSizeScale.get_value()
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
        if mp3_list is None:
            pass
        else:
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

        def callVoiceGenerator():
            if self.voiceOptionOn:
                voiceOutputList = self.voice.generateVoice(self.story_list[self.counterStoryParts])
            else: 
                voiceOutputList = None
            GLib.idle_add(lambda: updateGui(voiceOutputList))

        def updateGui(voiceOutputList):
            self.voiceOutputList = voiceOutputList
            self.imagePath = self.img_list[self.counterStoryParts]
            self.updateImage(None)
            self.result.get_buffer().set_text(self.story_list[self.counterStoryParts])
            self.pagesIndicatorNewText.set_text("{}/{}".format(self.counterStoryParts + 1, len(self.story_list)))
            self.playAudio(self.voiceOutputList)
            self.restoreButtonIcon(self.backButton)
            self.enterButton.set_sensitive(True)
            self.loadMessageHistButton.set_sensitive(True)
            self.saveMessageHistButton.set_sensitive(True)
            self.voiceRecognitionButton.set_sensitive(True)
            self.nextButton.set_sensitive(True)
            self.reenableToggle(self.backgroundVoiceSwitchButton)

        self.addSpinnerToButton(self.backButton)
        self.enterButton.set_sensitive(False)
        self.nextButton.set_sensitive(False)
        self.loadMessageHistButton.set_sensitive(False)
        self.saveMessageHistButton.set_sensitive(False)
        self.disableToggle(self.backgroundVoiceSwitchButton)
        self.voiceRecognitionButton.set_sensitive(False)
        threading.Thread(target=callVoiceGenerator).start()

    def actionNext(self, widget):
        if self.counterStoryParts == len(self.story_list) - 1:
            self.counterStoryParts = 0
        else:
            self.counterStoryParts += 1

        def callVoiceGenerator():
            if self.voiceOptionOn:
                voiceOutputList = self.voice.generateVoice(self.story_list[self.counterStoryParts])
            else: 
                voiceOutputList = None
            GLib.idle_add(lambda: updateGui(voiceOutputList))

        def updateGui(voiceOutputList):
            self.voiceOutputList = voiceOutputList
            self.imagePath = self.img_list[self.counterStoryParts]
            self.updateImage(None)
            self.result.get_buffer().set_text(self.story_list[self.counterStoryParts])
            self.pagesIndicatorNewText.set_text("{}/{}".format(self.counterStoryParts + 1, len(self.story_list)))
            self.playAudio(self.voiceOutputList)
            self.restoreButtonIcon(self.nextButton)
            self.enterButton.set_sensitive(True)
            self.loadMessageHistButton.set_sensitive(True)
            self.saveMessageHistButton.set_sensitive(True)
            self.backButton.set_sensitive(True)
            self.voiceRecognitionButton.set_sensitive(True)
            self.reenableToggle(self.backgroundVoiceSwitchButton)
        
        self.addSpinnerToButton(self.nextButton)
        self.enterButton.set_sensitive(False)
        self.backButton.set_sensitive(False)
        self.loadMessageHistButton.set_sensitive(False)
        self.saveMessageHistButton.set_sensitive(False)
        self.disableToggle(self.backgroundVoiceSwitchButton)
        self.voiceRecognitionButton.set_sensitive(False)
        threading.Thread(target=callVoiceGenerator).start()

    def addSpinnerToButton(self, button):
        self.spinner = Gtk.Spinner()
        if isinstance(button, Gtk.Button):
            self.tempOriginalButtonIcon = button.get_image()
            button.set_image(self.spinner)
            button.set_always_show_image(True)
        button.set_sensitive(False)
        self.spinner.start()
        self.show_all()
    
    def restoreButtonIcon(self, button):
        self.spinner.stop()
        if isinstance(button, Gtk.Button):
            button.set_image(self.tempOriginalButtonIcon)
        button.set_sensitive(True)
        self.show_all()

    def actionCallOllama(self, widget):
        def callTextGenerator(textGenerator, text, filePathToRead, model, interview_history, longTermMemory):
            if filePathToRead is not None:
                prompt = textGenerator.callImageReader(text, filePathToRead)
                filePathToRead = None
            else:
                prompt = text
            result = textGenerator.callOllama(prompt=prompt, message_hist=interview_history, model=model, db=longTermMemory)
            return result, interview_history

        def callLongTermMemoryWriter(textGenerator,
                                     interview_history,
                                     interview_history_max_length,
                                     writeToLongTermMemory,
                                     longTermMemory):
            if len(interview_history) > interview_history_max_length:
                writeToLongTermMemory()
                interview_history = interview_history[-interview_history_max_length:]
                longTermMemory = textGenerator.loadLongTermMemory(self.longTermMemoryPath)
            return interview_history, longTermMemory
        
        def callEmotionGenerator(createImageListFromEmotions, result_text, assistant):
            story_list = createStoryList(result_text)
            img_list = createImageListFromEmotions(story_list, assistant)
            return story_list, img_list
        
        def callVoiceGenerator(voice, story_list):
            voiceOutputList = voice.generateVoice(prompt=story_list[0])
            return voiceOutputList
        
        def callGenerators():
            result_text, interview_history = callTextGenerator(textGenerator=self.textGenerator,
                                                          text=self.enterText.get_text(), 
                                                          filePathToRead=self.filePathToRead, 
                                                          model=self.assistant.modelName, 
                                                          interview_history=self.interview_history,
                                                          longTermMemory=self.longTermMemory)
            interview_history, longTermMemory = callLongTermMemoryWriter(textGenerator=self.textGenerator,
                                                                        interview_history=interview_history,
                                                                        interview_history_max_length=self.interview_history_max_length,
                                                                        writeToLongTermMemory=self.writeToLongTermMemory,
                                                                        longTermMemory=self.longTermMemory)
            story_list, img_list = callEmotionGenerator(createImageListFromEmotions=self.createImageListFromEmotions,
                                                        result_text=result_text,
                                                        assistant=self.assistant)
            if self.voiceOptionOn:
                voiceOutputList = callVoiceGenerator(voice=self.voice, story_list=story_list)
            else:
                voiceOutputList = None
            result_dict = {
                'result_text' : result_text,
                'interview_history' : interview_history,
                'longTermMemory' : longTermMemory,
                'story_list' : story_list,
                'img_list' : img_list,
                'voiceOutputList' : voiceOutputList
            }
            GLib.idle_add(lambda: updateVariables(result_dict))
            GLib.idle_add(lambda: updateGui())

        def updateVariables(result_dict):
            self.result_text = result_dict['result_text']
            self.interview_history = result_dict['interview_history']
            self.longTermMemory = result_dict['longTermMemory']
            self.story_list = result_dict['story_list']
            self.img_list = result_dict['img_list']
            self.voiceOutputList = result_dict['voiceOutputList']
        
        def updateGui():
            self.counterStoryParts = 0
            if self.counterEnter == 0:
                self.createTextResultsBox()
                self.createBackAndNextButtons()
            self.pagesIndicatorNewText.set_text("{}/{}".format(self.counterStoryParts + 1, len(self.story_list)))
            self.counterEnter = 1
            self.result.get_buffer().set_text(self.story_list[0])
            self.imagePath = self.img_list[0]
            self.updateImage(None)
            self.playAudio(self.voiceOutputList)
            self.restoreButtonIcon(self.enterButton)
            self.nextButton.set_sensitive(True)
            self.backButton.set_sensitive(True)
            self.loadMessageHistButton.set_sensitive(True)
            self.saveMessageHistButton.set_sensitive(True)
            self.voiceRecognitionButton.set_sensitive(True)
            self.reenableToggle(self.backgroundVoiceSwitchButton)
        
        self.addSpinnerToButton(self.enterButton)
        if self.counterEnter != 0:
            self.nextButton.set_sensitive(False)
            self.backButton.set_sensitive(False)
        self.loadMessageHistButton.set_sensitive(False)
        self.saveMessageHistButton.set_sensitive(False)
        self.disableToggle(self.backgroundVoiceSwitchButton)
        self.voiceRecognitionButton.set_sensitive(False)
        threading.Thread(target=callGenerators).start()
                        
    def writeToLongTermMemory(self):
        if self.isFirstTimeWritingToLongTermMemory == 0:
            if self.longTermMemoryPath is None:
                self.messagesToWrite = self.interview_history
            else:
                self.messagesToWrite = self.interview_history[-3:]
            self.isFirstTimeWritingToLongTermMemory = 1
        else:
            self.messagesToWrite = self.interview_history[-2:]
        if self.longTermMemoryPath is None:
            self.longTermMemoryPath = "long_term_memory_temp.txt"
            ltm = open(self.longTermMemoryPath, "a")
            ltm.truncate(0)
        else:
            ltm = open(self.longTermMemoryPath, "a")
        for message_i in self.messagesToWrite:
            message = message_i['content'].replace('\n\n', ' ').replace('\n', ' ')
            if message_i['role'] == 'assistant':
                role = self.assistant.modelName
                string_to_write = f'''\n{role} said: {message}'''
            else:
                role = message_i['role']
                string_to_write = f'''\n\n{role} said: {message}'''
            ltm.write(str(string_to_write))
        ltm.close()        
            
    
    def createImageListFromEmotions(self, story_list: list[str], assistantClass):
        img_list = []
        for story_i in story_list:
            emotion_i = self.textGenerator.defineEmotionUsingEmbeddings(story_i, assistantClass.emotionsList)
            image_path = assistantClass.imagesPaths[emotion_i]
            img_list.append(image_path)
        return img_list

def main():
    def onWindowDestroy(window):
        app.backgroundVoiceSwitchButton.set_active(False)
        return Gtk.main_quit()
    
    app = Application()
    app.connect("destroy", onWindowDestroy)
    app.show_all()
    Gtk.main()




if __name__ == "__main__":
    main()
