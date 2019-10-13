#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
import os
import os.path
import commands
from datetime import timedelta
from subprocess import Popen, PIPE, STDOUT

from PyQt4.QtGui import *
from PyQt4.QtCore import *
#from PyQt5.QtWidgets import *

app_name = "StreamCap"
app_version = "0.1.3"
app_author = "olivier Girard"
author_email = "olivier@openshot.org"


class StreamCap(QMainWindow):
    """
	Here the main class of the application with his creation, connect all signals etc..
	"""

    def __init__(self, parent=None):
        """
		Constructor
		"""
        super(QMainWindow, self).__init__(parent)

        self.default_size = QSize(633, 410)
        self.default_position = QPoint(20, 20)

        self.DiscName = None

        self.ExplicitPathSpecified = False
        self.ParserVobcopy = VobCopyParser(self)

        #===============================================================================================================
        #init some event handlers
        self.connect(self.ParserVobcopy, SIGNAL("TraceMessage(QString)"), self.LogInfo)
        self.connect(self.ParserVobcopy, SIGNAL("CaptureProgress(int)"), self.UpdateProgress)

        #============================================================================
        self.SetupUi()

        #============================================================================
        settings = QSettings()
        size_screen = settings.value("MainWindow/Size", QVariant(self.default_size)).toSize()
        self.resize(size_screen)
        position_screen = settings.value("MainWindow/Position", QVariant(self.default_position)).toPoint()
        self.move(position_screen)
        if settings.value("MainWindow/IsMaximised", QVariant(False)).toBool() == True:
            self.showMaximized()

        output_path = settings.value("MainWindow/OutputPath", QVariant(os.getenv("HOME"))).toString()
        self.lneoutputpath.setText(output_path)

        self.restoreState(settings.value("MainWindow/State").toByteArray())

        #=============================================================================
        self.ReadDiscInfo()

        #=================================================================================


    def closeEvent(self, event):
        """
        Here we close correctly the application and write all settings for using them the next time like his size, the output path
        """

        settings = QSettings()

        size_window = QVariant(self.size())
        position_window = QVariant(self.pos())
        window_ismaximised = QVariant(False)

        if self.isMaximized() == True:
            window_ismaximised = QVariant(True)
            size_window = QVariant(self.default_size)
            position_window = QVariant(self.default_position)

        settings.setValue("MainWindow/IsMaximised", window_ismaximised)
        settings.setValue("MainWindow/Size", size_window)
        settings.setValue("MainWindow/Position", position_window)
        settings.setValue("MainWindow/OutputPath", QVariant(self.lneoutputpath.text()))
        settings.setValue("MainWindow/State", QVariant(self.saveState()))

        #==================================================================================


    def SetupUi(self):
        """
        Here this method design the gui
        and restore the size
        """
        self.resize(self.default_size)

        wgCentral = QWidget(self)
        vlayout1 = QVBoxLayout(wgCentral)

        #Devices groupbox
        gbDevice = QGroupBox(self.tr("Device Info"))
        hlayDevGb = QHBoxLayout(gbDevice)
        labDevPath = QLabel(self.tr("Device Path"))
        self.lnedevicepath = QLineEdit()
        labDevMont = QLabel(self.tr("Mount Point"))
        self.lnedevicemount = QLineEdit()
        self.btnrefreshdevice = QPushButton(self.tr("Refresh"))
        hlayDevGb.addWidget(labDevPath)
        hlayDevGb.addWidget(self.lnedevicepath)
        hlayDevGb.addWidget(labDevMont)
        hlayDevGb.addWidget(self.lnedevicemount)
        hlayDevGb.addWidget(self.btnrefreshdevice)

        vlayout1.addWidget(gbDevice)

        #=====================================================================================
        #Disc Details Groupbox
        gbDisc = QGroupBox(self.tr("Disc Details"))
        hlayDiscGb = QHBoxLayout(gbDisc)
        self.lbldiscname = QLabel(self.tr("Disc name:"))
        self.lbltitlecount = QLabel(self.tr("Title count:"))
        hlayDiscGb.addWidget(self.lbldiscname)
        hlayDiscGb.addWidget(self.lbltitlecount)

        vlayout1.addWidget(gbDisc)

        #=====================================================================================
        #Titles Groupbox
        gbTitles = QGroupBox(self.tr("Titles"))
        vlayTitlesGb = QVBoxLayout(gbTitles)

        hlayTitlesButtons = QHBoxLayout()

        self.ListTitles = CheckedListBox()
        vlayTitlesGb.addWidget(self.ListTitles)

        self.btncopytitles = QPushButton(self.tr("Copy titles"))

        self.progressbarcapture = QProgressBar()
        self.progressbarcapture.setRange(0, 100)
        self.progressbarcapture.setEnabled(True)
        self.UpdateProgress(0)

        hlayTitlesButtons.addWidget(self.progressbarcapture)
        hlayTitlesButtons.addWidget(self.btncopytitles)
        vlayTitlesGb.addLayout(hlayTitlesButtons)
        vlayout1.addWidget(gbTitles)

        #=========================================================================================
        #Output destination groupbox
        gbOutput = QGroupBox(self.tr("Output Destination"))
        hlayOutput = QHBoxLayout(gbOutput)

        laboutputpath = QLabel(self.tr("Output Path"))
        self.lneoutputpath = QLineEdit()
        self.btnchooseoutputpath = QPushButton(self.tr("..."))

        hlayOutput.addWidget(laboutputpath)
        hlayOutput.addWidget(self.lneoutputpath)
        hlayOutput.addWidget(self.btnchooseoutputpath)

        vlayout1.addWidget(gbOutput)

        #============================================================================================
        #fichier log
        self.textlog = QTextEdit()
        self.textlog.setReadOnly(True)
        self.textlog.setLineWrapMode(QTextEdit.NoWrap)

        vlayout1.addWidget(self.textlog)

        #=======================================================================================
        #setup toolbar
        mnuBar = QMenuBar()
        mnuFile = QMenu(self.tr("&File"), mnuBar)

        self.mnuFileExit = QAction(self.tr("E&xit"), mnuFile)
        self.mnuFileRefreshDiscInfo = QAction(self.tr("&Refresh Disc Info"), mnuFile)

        mnuFile.addAction(self.mnuFileRefreshDiscInfo)
        mnuFile.addSeparator()
        mnuFile.addAction(self.mnuFileExit)

        self.setMenuBar(mnuBar)
        mnuBar.addAction(mnuFile.menuAction())

        #final form
        self.setCentralWidget(wgCentral)
        self.setWindowTitle(self.tr("StreamCap"))

        #============================================================================================
        #init event handlers
        self.connect(self.mnuFileExit, SIGNAL("activated()"), self, SLOT("close()"))
        self.connect(self.mnuFileRefreshDiscInfo, SIGNAL("activated()"), (self.RefreshDev))
        self.connect(self.btnrefreshdevice, SIGNAL("clicked()"), (self.RefreshDev))
        self.connect(self.btncopytitles, SIGNAL("clicked()"), (self.CopyTitles))
        self.connect(self.btnchooseoutputpath, SIGNAL("clicked()"), (self.BrowseOutputPath))

        #=============================================================================================
    def RefreshDev(self):
        """
        Here we refresh the list of devices, mount point and title of dvd and numbers of tracks
        """

        if len(self.lnedevicepath.text()) != 0: #aucun text n' est ici
            self.ExplicitPathSpecified = True
            self.ListDevices = []
            self.ListDevices.append(unicode(self.lnedevicepath.text()))
            self.ListDevices.append(unicode(self.lnedevicemount.text()))

        #clear list box
        self.ListTitles.Clear()
        self.ReadDiscInfo()
        #================================================================================================
    def CopyTitles(self):
        """
        Here we copy titles, see the progression and remove a file if the same file already exist
        """

        aTitlesData = self.ListTitles.GetSelecteddata()

        for oProps in aTitlesData:
            self.UpdateProgress(0)
            #figure out if the output file exists
            output_dir = unicode(self.lneoutputpath.text())
            outputfilepath = os.path.join(output_dir, "%s%i.vob" % (self.DiscName, int(oProps["TITLE"])))

            if os.path.exists(outputfilepath):
                #if a path exist remove it
                self.LogInfo("[StreamCap] File '%s' already exists. Removing" % (outputfilepath))
                os.remove(outputfilepath)

            #then do the rip
            self.ParserVobcopy.CaptureStream(self.ListDevices[1], oProps["TITLE"], output_dir)

            #=============================================================================================
    def BrowseOutputPath(self):
        """
        Here we get the output path and display it in the line label corresponding
        """

        output_path = QFileDialog.getExistingDirectory(self, self.tr("Choose output path"), self.lneoutputpath.text())

        if len(output_path) > 0:
            self.lneoutputpath.setText(output_path)

        #=================================================================================================
    def ReadDiscInfo(self):
        """
        Here we read the disc, display information who are set in different lables like mount poin, devices and title
        and number of tracks
        """

        try:
            if self.ExplicitPathSpecified == False:
                self.ListDevices = self.ParserVobcopy.GetDevicePath()

            if len(self.ListDevices) > 0:
                self.lnedevicepath.setText(self.ListDevices[0])
                self.lnedevicemount.setText(self.ListDevices[1])

                aProps = self.ParserVobcopy.GetTitleProperties(self.ListDevices[0])
                self.lbldiscname.setText("Disc Name: <b>%s</b>" % aProps["DISCNAME"])
                self.DiscName = aProps["DISCNAME"]
                self.lbltitlecount.setText("Title count: <b>%s</b>" % len(aProps["TITLES"]))

                #build titles list
                firsttitle = True

                for aTitleProps in aProps["TITLES"]:
                    titlestring = "Title: %s Duration: %s" % (aTitleProps["TITLE"], aTitleProps["LENGTH"])
                    ocheck = self.ListTitles.AddCheckBox(titlestring, aTitleProps)

                    if firsttitle == True:
                        ocheck.setChecked(True)
                        firsttitle = False

            else:
                self.LogInfo(self.tr("Couldn't find mounted DVD"))

        except Exception as ex:
            raise ex
            messageerror = "[ERROR] %s" % ex
            print ("messageerror")
            self.LogInfo(messageerror)

        #===============================================================================================
    def LogInfo(self, logText):
        """
        Here we display all messages from all others functions and of vobcopy and his progress
        """

        self.textlog.append(logText)
        self.textlog.repaint()

        #===============================================================================================
    def UpdateProgress(self, progress):
        """
        Here we display the value of the progression of the progressbar
        """

        self.progressbarcapture.setValue(progress)

        self.progressbarcapture.repaint()

        #==================================================================================================
    def Version(self):
        """
        Here we get the version of the application StreamCap
        """

        return app_version

        #==================================================================================================

class CheckedListBox(QFrame):
    """
    This class create the list of checkbox in the gui
    """

    def __init__(self, parent=None):
        super(QFrame, self).__init__(parent)

        #region set up layout
        self.setFrameShape(QFrame.WinPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setMidLineWidth(1)
        self.setLineWidth(1)

        self.scrollframe = QFrame()
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.StyledPanel)
        scroll.setFrameShadow(QFrame.Sunken)

        mainlayout = QVBoxLayout()
        mainlayout.setMargin(0)

        self.scrolllay = QVBoxLayout()
        self.scrolllay.setSpacing(0)
        self.scrolllay.setSizeConstraint(QLayout.SetMinimumSize)

        self.scrollframe.setLayout(self.scrolllay)
        scroll.setWidget(self.scrollframe)

        mainlayout.addWidget(scroll)
        self.setLayout(mainlayout)

        #varialbles
        self.checkedbox = []
        self.datatitle = []

        #====================================================================================================
    def AddCheckBox(self, boxtext, data=None):
        """
        Here we create chekcbox in the gui
        """

        ocheck = QCheckBox(boxtext)
        self.scrolllay.addWidget(ocheck)
        self.checkedbox.append(ocheck)
        self.datatitle.append(data)

        return ocheck

    #===================================================================================================
    def GetSelecteddata(self):
        """
        Here we get all datas
        """

        i = 0
        areturn = []
        for ocheck in self.checkedbox:
            if ocheck.isChecked() == True:
                areturn.append(self.datatitle[i])
            i += 1

        return areturn

    #==========================================================================================================
    def Clear(self):
        """
        Here we clear all checkedbox when the user want to refresh the dvd point and the result of this action
        """

        for ocheck in self.checkedbox:
            ocheck.setParent(None)
            del ocheck

        self.checkedbox = []
        self.datatitle = []

        self.repaint()

    #=============================================================================================================
class VobCopyParser(QObject):
    """
    This class define how to  parser and copy streams of a dvd
    """

    def __index__(self, parent=None):

        super(QObject, self).__init__(parent)

        if self.TestVobCopy() == 0:
            raise Exception(self.tr("Couldn't find Vobcopy. Is it installed ?"))

        if self.TestLsdvd() == 0:
            raise Exception(self.tr("Couldn't find Lsdvd. Is it installed ?"))

    #===================================================================================================================

    def OnTraceMessage(self, message):
        """
        Here we grab all signals emitted by vobcopy and put them in the textedit
        """

        self.emit(SIGNAL("TraceMessage(QString)"), message)

    #===========================================================================================================

    def OnCaptureProgress(self, percent):
        """
        Here we grab the progression in percent of the progressbar
        """

        self.emit(SIGNAL("CaptureProgress(int)"), percent)

    #==============================================================================================================
    #check dependencies
    def TestVobCopy(self):
        """
        Here we test if vobcopy is installed
        """

        resultcommand = commands.getstatusoutput("which vobcopy")

        if resultcommand[0] != 0:
            return 0
        return 1

    #===================================================================================================================
    def TestLsdvd(self):
        """
        Here we test if lsdvd is installed
        """

        resultcommand = commands.getstatusoutput("which lsdvd")

        if resultcommand[0] != 0:
            return 0
        return 1

    #===================================================================================================================
    def GetDevicePath(self):
        """
        Here we get the device path
        mount it
        """

        vobcopy_command = "vobcopy -I"
        resultcommand = commands.getstatusoutput(vobcopy_command)

        if resultcommand[0] != 0:
            return []

        alllines = resultcommand[1].splitlines()

        #target line should looks like this: [info] Path to dvd : /dev/sr0/
        areturn = []
        devicepath = ""

        self.OnTraceMessage("[StreamCap] starting GetDevicePath: <b><i>%s</i></b>" % vobcopy_command)

        for Line in alllines:
            self.OnTraceMessage(Line)
            if Line.upper().find("PATH TO DVD") != -1:
                devicepath = Line.split(":")[1].strip()
                areturn.append(devicepath)

        #mount | grep /dev/sr0
        mount_command = "mount | grep %s" % devicepath
        resultcommand = commands.getstatusoutput(mount_command)

        if resultcommand[0] != 0:
            return []
        alllines = resultcommand[1].splitlines()
        for Line in alllines:
            if Line.upper().find(devicepath.upper()) != -1:
                areturn.append(Line.split(" ")[2])
                break

        return areturn

    #===================================================================================================================
    def GetTitleProperties(self, device):
        """
        Here we get all properties of the dvd
        """
        lsdvd_command = "lsdvd %s" % (device)

        self.OnTraceMessage("[StreamCap] Starting GetTitleProperties: <b><i>%s</i></b>" % lsdvd_command)

        lsdvdresultcommand = commands.getstatusoutput(lsdvd_command)
        if lsdvdresultcommand[0] != 0:
            return []

        alllines = lsdvdresultcommand[1].splitlines()

        aProps = {}
        atitles = []
        for Line in alllines:
            Line = Line.upper().replace("CHAPTERS", ",CHAPTERS") #deal with the lack of a comma
            if len(Line) > 0:
                #lets ignore those blanklines
                self.OnTraceMessage(Line)

            if Line.startswith("TITLE"):
                atitlesproperties = {}
                anamevaluepairs = Line.split(",")

                for namevalue in anamevaluepairs:
                    newnamevalue = namevalue.split(":", 1) #only split the first one to preserve to time string
                    atitlesproperties[newnamevalue[0].strip()] = newnamevalue[1].strip()
                atitlesproperties["LENGTH"] = self.ParseTimeDelta(atitlesproperties["LENGTH"])
                atitles.append(atitlesproperties)
            elif Line.startswith("DISC TITLE:"):
                aProps["DISCNAME"] = Line.split(":")[1].strip()

        aProps["TITLES"] = self.SortTitles(atitles)
        return aProps

    #===================================================================================================================
    def CaptureStream(self, device, title, output_dir):
        """
        Here we run the process to capture the dvd. We get the output trace, apply it in the textedit, run
        the progress bar, see his progress until the rip will be finished
        """
        vobcopy_command = "vobcopy -i %s -n %s -o %s -l" % (device, title, output_dir)

        self.OnTraceMessage("[StreamCap] Starting CaptureStream: <b><i>%s</i></b>" % vobcopy_command)

        process = Popen(vobcopy_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, bufsize=1)
        Line = ""
        continueprocess = True
        while continueprocess == True:
            character = process.stdout.read(1)

            if character == "\n" or character == "\r":
                if Line.find("written") == -1:
                    self.OnTraceMessage(Line)
                else:
                    #display the progress of the progressbar style "37MB of 215MB written (17 %)"
                    percent = int(Line.split("(")[1].replace(".", " ").strip().split(" ")[0])

                    self.OnCaptureProgress(percent)

                    Line = ""

            else:
                Line += character

            if Line.find("[Hint] Have a lot of fun!") != -1:
                continueprocess = False

        self.OnCaptureProgress(100)

    #===================================================================================================================
    def SortTitles(self, titles):
        """
        Here we sort all titles following their length, the most long in first
        """

        #sort descending on LENGTH
        sortedtitles = 0
        while sortedtitles == 0:
            sortedtitles = 1
            for i in range(1, len(titles)):
                if titles[i-1]["LENGTH"] < titles[i]["LENGTH"]:
                    sortedtitles = 0
                    atmp = titles[i-1]
                    titles[i-1] = titles[i]
                    titles[i] = atmp

        return titles

    #===================================================================================================================
    def ParseTimeDelta(self, timeString):
        """
        Here we get the time in a format style appropriated
        """

        #format style 00:00:34:140
        atime = timeString.split(":")
        asecs = atime[2].split(".")

        return timedelta(hours=int(atime[0]), minutes=int(atime[1]), seconds=int(asecs[0]), milliseconds=int(asecs[1]))

    #===================================================================================================================
if __name__ == "__main__":
    application = QApplication(sys.argv)
    # Translate application
    translator = QTranslator()
    if len(sys.argv) == 1:
        locale = QLocale()
        translator.load(locale, "streamcap", ".")
    else:
        translator.load("streamcap." + sys.argv[1])

    StreamCap = StreamCap()
    if "v" in sys.argv or "--version" in sys.argv:
        print ("StreamCap version %s") % StreamCap.Version()
        sys.exit(0)
    StreamCap.show()
    sys.exit(application.exec_())
