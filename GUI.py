from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QWidget, QInputDialog,
                             QAction, QFileDialog, QApplication, QLineEdit,
                             QFileDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             )
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtCore import QObject, pyqtSignal
import sys
from pathlib import Path
from os import listdir, getcwd, walk, makedirs
from os.path import isfile, join, splitext
from PIL import Image, UnidentifiedImageError
from pyautogui import locateOnScreen, screenshot, locate


class Stream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class MainGUI(QMainWindow):

    def __init__(self):
        super().__init__()

        # initialize variables (needed outside this class)
        self.templatefilepath = None
        self.outputfolderpath = None
        self.startingfolderpath = None

        # initialization of variables related to the image
        self.templateimage = None
        self.comparisonimage = None
        self.confidenceparameter = 0.9

        # Layout Initialization
        self.QVBox_mainLayout = QVBoxLayout()
        self.QHBox_searchPathLayout = QHBoxLayout()
        self.QHBox_templateFileLayout = QHBoxLayout()
        self.QHBox_outputFolderLayout = QHBoxLayout()
        self.QHBox_confidenceLayout = QHBoxLayout()
        self.QHBox_consoleOutLayout = QHBoxLayout()
        self.QHBox_controlButtons = QHBoxLayout()

        # Individual components (=> must match with add widgets below)
        self.QLine_startingDirectoryPath = QLineEdit()
        self.QPBtn_startingDirectoryLoad = QPushButton("Load", self)
        self.QPBtn_startingDirectoryBrowse = QPushButton("Browse", self)

        self.QLine_templateFilePath = QLineEdit()
        self.QPBtn_templateFileLoad = QPushButton("Load", self)
        self.QPBtn_templateFileBrowse = QPushButton("Browse", self)

        self.QLine_outputFolderPath = QLineEdit()
        self.QPBtn_outputFolderLoad = QPushButton("Load", self)
        self.QPBtn_outputFolderBrowse = QPushButton("Browse", self)

        self.QLine_currentConfidenceValue = QLineEdit()
        self.QLine_currentConfidenceValue.setText(str(self.confidenceparameter))
        self.QLine_newConfidenceValue = QLineEdit()
        self.QPBtn_changeConfidence = QPushButton("Change Confidence", self)
        self.QPBtn_defaultConfidence = QPushButton("Default Confidence", self)

        self.QText_consoleProcess = QTextEdit()
        self.QText_consoleProcess.moveCursor(QTextCursor.Start)
        self.QText_consoleProcess.ensureCursorVisible()
        self.QText_consoleProcess.setLineWrapColumnOrWidth(500)
        self.QText_consoleProcess.setLineWrapMode(QTextEdit.FixedPixelWidth)

        self.QPBtn_runProgram = QPushButton("Run Search", self)
        self.QPBtn_exitProgram = QPushButton("Exit", self)

        # Adds the widgets to the layout (=> must match with individual components above)
        self.QHBox_searchPathLayout.addWidget(self.QLine_startingDirectoryPath)
        self.QHBox_searchPathLayout.addWidget(self.QPBtn_startingDirectoryLoad)
        self.QHBox_searchPathLayout.addWidget(self.QPBtn_startingDirectoryBrowse)

        self.QHBox_templateFileLayout.addWidget(self.QLine_templateFilePath)
        self.QHBox_templateFileLayout.addWidget(self.QPBtn_templateFileLoad)
        self.QHBox_templateFileLayout.addWidget(self.QPBtn_templateFileBrowse)

        self.QHBox_outputFolderLayout.addWidget(self.QLine_outputFolderPath)
        self.QHBox_outputFolderLayout.addWidget(self.QPBtn_outputFolderLoad)
        self.QHBox_outputFolderLayout.addWidget(self.QPBtn_outputFolderBrowse)

        self.QHBox_confidenceLayout.addWidget(QLabel("The current confidence value is : "))
        self.QHBox_confidenceLayout.addWidget(self.QLine_currentConfidenceValue)
        self.QHBox_confidenceLayout.addWidget(QLabel("Change the confidence value to : "))
        self.QHBox_confidenceLayout.addWidget(self.QLine_newConfidenceValue)
        self.QHBox_confidenceLayout.addWidget(self.QPBtn_changeConfidence)
        self.QHBox_confidenceLayout.addWidget(self.QPBtn_defaultConfidence)

        self.QHBox_consoleOutLayout.addWidget(self.QText_consoleProcess)

        self.QHBox_controlButtons.addWidget(self.QPBtn_runProgram)
        self.QHBox_controlButtons.addWidget(self.QPBtn_exitProgram)
        # When finished here, check layout mainUILayout below

        # Attaching all methods
        self.initUI()
        self.mainUILayout()
        self.menusAndActions()

        # TOGGLE COMMENT/UNCOMMENT TO (NOT USE)/USE GUI TEXTBOX IN CONSOLE
        # NEEDS FURTHER WORK WITH MULTITHREADING/PROCESSING
        sys.stdout = Stream(newText=self.onUpdateText)

    def initUI(self):
        widget = QWidget()
        widget.setLayout(self.QVBox_mainLayout)
        self.setCentralWidget(widget)

        self.statusBar()

        self.setGeometry(300, 300, 1000, 700)
        self.setWindowTitle("Template Searching Tool")
        self.show()

    def __del__(self):
        sys.stdout = sys.__stdout__

    # QVBox Components here
    def mainUILayout(self):
        self.QVBox_mainLayout.addWidget(QLabel("Path to start searching from : "))
        self.QVBox_mainLayout.addLayout(self.QHBox_searchPathLayout)

        self.QVBox_mainLayout.addWidget(QLabel("Template(picture) to search for : "))
        self.QVBox_mainLayout.addLayout(self.QHBox_templateFileLayout)

        self.QVBox_mainLayout.addWidget(QLabel("Path to save all found images to : "))
        self.QVBox_mainLayout.addLayout(self.QHBox_outputFolderLayout)

        self.QVBox_mainLayout.addLayout(self.QHBox_confidenceLayout)

        self.QVBox_mainLayout.addLayout(self.QHBox_consoleOutLayout)

        self.QVBox_mainLayout.addLayout(self.QHBox_controlButtons)

    def menusAndActions(self):
        # For all the buttons and their actions
        # self.QPBtn_startingDirectoryLoad.clicked.connect(self.clickme) // Need to add function for loading
        self.QPBtn_startingDirectoryBrowse.clicked.connect(self.showStartingFolderSelectDialog)

        # self.QPBtn_templateFileLoad.clicked.connect(self.clickme) // Need to add function for loading
        self.QPBtn_templateFileBrowse.clicked.connect(self.showTemplateFileSelectDialog)

        # self.QPBtn_outputFileLoad.clicked.connect(self.clickme) // Need to add function for loading
        self.QPBtn_outputFolderBrowse.clicked.connect(self.showOutputFolderSelectDialog)

        self.QPBtn_changeConfidence.clicked.connect(self.changeConfidence)
        self.QPBtn_defaultConfidence.clicked.connect(self.setDefaultConfidence)

        self.QPBtn_runProgram.clicked.connect(self.checkBeforeSearch)
        self.QPBtn_exitProgram.clicked.connect(self.exitProgram)

        # SHOWN BELOW ARE ACTIONS
        # Open a File(NEEDS ORGANIZING)
        openFile = QAction(QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showTemplateFileSelectDialog)

        # Exit the Program
        exitProgram = QAction(QIcon('exit.png'), 'Exit', self)
        exitProgram.setShortcut('Alt+F4')
        exitProgram.setStatusTip('Close the Program')
        exitProgram.triggered.connect(self.exitProgram)

        # ALL ACTIONS MUST BE ADDED HERE TO BE SHOWN IN THE MENU BAR
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(exitProgram)

    def onUpdateText(self, text):
        cursor = self.QText_consoleProcess.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.QText_consoleProcess.setTextCursor(cursor)
        self.QText_consoleProcess.ensureCursorVisible()

    def showStartingFolderSelectDialog(self):
        home_dir = str(Path.home())
        self.startingfolderpath = QFileDialog.getExistingDirectory(self, 'Initial Search Directory', home_dir)
        if self.startingfolderpath:
            self.QLine_startingDirectoryPath.setText(self.startingfolderpath)

    def showTemplateFileSelectDialog(self):
        home_dir = str(Path.home())
        self.templatefilepath = QFileDialog.getOpenFileName(self, 'Select Template File', home_dir)
        if self.templatefilepath[0]:
            self.QLine_startingDirectoryPath.setText(self.templatefilepath[0])

    def showOutputFolderSelectDialog(self):
        home_dir = str(Path.home())
        self.outputfolderpath = QFileDialog.getOpenFileName(self, 'Select Output Directory', home_dir)
        if self.outputfolderpath[0]:
            self.QLine_outputFolderPath.setText(self.outputfolderpath[0])

    def changeConfidence(self):
        self.confidenceparameter = self.QLine_newConfidenceValue.text()
        self.QLine_currentConfidenceValue.setText(str(self.confidenceparameter))

    def setDefaultConfidence(self):
        self.confidenceparameter = 0.90
        self.QLine_currentConfidenceValue.setText(str(self.confidenceparameter))

    def checkBeforeSearch(self):
        if self.outputfolderpath == None:
            print("Please enter a path to save the images to")
            pass
        elif self.templatefilepath == None:
            print("Please enter a template(picture) to search for")
            pass
        elif self.startingfolderpath == None:
            print("Please enter a path to start searching from")
            pass
        else:
            self.searchForTemplate()

    def searchForTemplate(self):
        print("Starting Search")
        self.comparisonimage = None
        self.templateimage = None
        try:
            print(self.templatefilepath[0])
            self.templateimage = Image.open(str(self.templatefilepath[0]))
            self.walkFiles()
        except UnidentifiedImageError:
            print("There's something wrong with the template image. Try again.")
            pass

    def walkFiles(self):
        self.QText_consoleProcess.clear()
        print("Starting search...")
        for root, dirs, files in walk(str(self.startingfolderpath), topdown=True):
            for file_found in files:
                if file_found.endswith(('.gif', '.png', '.jpeg', '.jpg')):
                    try:
                        self.comparisonimage = Image.open(str(Path(root) / file_found))
                        try:
                            validImageFlag = locate(self.templateimage, self.comparisonimage,
                                                    grayscale=True, confidence=self.confidenceparameter)
                            if validImageFlag is not None:
                                print("Iamge located : " + str(Path(self.outputfolderpath)))
                                try:
                                    self.comparisonimage.save(Path(self.outputfolderpath) / file_found)
                                    print("Saved file")
                                except FileExistsError:
                                    pass
                        except Exception as e:
                            print("Something went wrong while locating within this image : "
                                  + str(Path(root) / file_found) + " : " + str(e))
                            pass
                    except UnidentifiedImageError:
                        pass
                else:
                    pass
        print("Finished searching!")

    # Currently not being used
    def showTemplateImage(self):
        self.templateimage.show()

    def exitProgram(self):
        sys.exit()
