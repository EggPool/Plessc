#!/usr/bin/env python3
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os,sys,subprocess

from ui_MainWindow import Ui_MainWindow
from settings import SettingDialog
import sip

class MainWindow ( QMainWindow , Ui_MainWindow):

    #var initialization
    settings = QSettings('Mte90','Plessc')
    settings.setFallbacksEnabled(False)
    version = 'V 1.0 Beta'
    input_less = ''
    output_css = ''
    save_method = 0
    mysize = ''

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle('PLessc - ' + self.version)
        self.ui.inputChoose.clicked.connect(self.openInputDialog)
        self.ui.outputChoose.clicked.connect(self.openOutputDialog)
        self.ui.setMinify.pressed.connect(self.setMinify)
        self.ui.setYUI.pressed.connect(self.setYUICompress)
        self.ui.setBoth.pressed.connect(self.setBoth)
        self.ui.setStandard.pressed.connect(self.setStandard)
        self.ui.inputEdit.pressed.connect(self.openEditor)
        self.ui.outputLog.clicked.connect(self.openLog)
        self.ui.compile.clicked.connect(self.compileIt)
        self.ui.menuInfo.triggered.connect(self.openInfo)
        self.ui.menuSetting.triggered.connect(self.openSetDialog)
        #hide log
        self.ui.log.hide()
        if self.settings.value('input_file') != -1:
            self.input_less = self.settings.value('input_file').toString()
        else:
            self.input_less = '/'
        if self.settings.value('output_file') != -1:
            self.output_css = self.settings.value('output_file').toString()
        else:
            self.output_css = '/'
        self.ui.inputFile.setText(self.input_less)
        self.ui.outputFile.setText(self.output_css)
        if self.settings.contains('min_or_yui') == False or self.settings.value('min_or_yui').toBool() == False:
            minify_option = '--yui-compress ';
            self.settings.setValue('min_or_yui',False)
            self.ui.setYUI.toggle()
        else:
            self.minify_option = '-x '
            self.settings.setValue('min_or_yui',True)
            self.ui.setMinify.toggle()
        if self.settings.contains('both_or_standard') == False or self.settings.value('both_or_standard').toBool() == False:
            self.save_method = 0
            self.settings.setValue('both_or_standard',False)
            self.ui.setStandard.toggle()
        else:
            self.save_method = 1
            self.settings.setValue('both_or_standard',True)
            self.ui.setBoth.toggle()
        self.resize(503,213)
        self.show()

    def openInputDialog(self):
        self.input_less = QFileDialog.getOpenFileName(self, 'Choose less file',self.ui.inputFile.text(),'LESS file (*.less)')
        self.ui.inputFile.setText(self.input_less)
        self.settings.setValue('input_file',self.input_less)

    def openOutputDialog(self):
        self.output_css = QFileDialog.getSaveFileName(self, 'Set css file',self.ui.outputFile.text(),'CSS file (*.css)')
        self.ui.outputFile.setText(self.output_css)
        self.settings.setValue('output_file',self.output_css)

    def setMinify(self):
        self.minify_option = '-x '
        self.settings.setValue('min_or_yui',True)

    def setYUICompress(self):
        self.minify_option = '--yui-compress '
        self.settings.setValue('min_or_yui',False)

    def setBoth(self):
        self.save_method = 1
        self.settings.setValue('both_or_standard',True)

    def setStandard(self):
        self.save_method = 0
        self.settings.setValue('both_or_standard',False)

    def compileIt(self):
        if self.save_method == 1:
            name = self.settings.value('output_file').toString()
            name.replace('.css','.min.css')
            command = str(self.settings.value('less_path').toString() + ' --verbose "' + self.settings.value('input_file').toString() + '" > "' + self.settings.value('output_file').toString() + '"')
            os.system(str(self.settings.value('less_path').toString() + ' ' + self.minify_option + '"' + self.settings.value('input_file').toString() + '" > "' + name + '"' ))
            stdout = os.popen4(command)[1].read()
            print stdout
            stdout = self.replace_all(stdout)
            self.ui.log.setHtml(stdout)
            self.ui.info.setText('File Min Output: ' + self.sizeof_fmt(name) + ' | File Standard: ' + self.sizeof_fmt(self.settings.value('output_file').toString()))
        else:
            command = str(self.settings.value('less_path').toString() + ' ' + self.minify_option + '"' + self.settings.value('input_file').toString() + '" > "' + self.settings.value('output_file').toString() + '"' )
            stdout = os.popen4(command)[1].read()
            print stdout
            stdout = self.replace_all(stdout)
            self.ui.log.setHtml(stdout)
            self.ui.info.setText('File Output: <b>' + self.sizeof_fmt(self.settings.value('output_file').toString()) + '</b>')
        print command

    def openEditor(self):
        open_file = self.settings.value('input_file').toString()
        if self.settings.value('less_folder').toBool() == True:
            list_file = ''
            path_less = os.path.split(str(open_file))[0]
            for root, dirs, files in os.walk(path_less):
                files.sort()
                for name in files:
                    filename = os.path.join(root, name)
                    list_file = list_file + '"' + filename + '" '
            open_file = list_file
        os.system(str(self.settings.value('editor_path').toString() + ' ' + open_file))

    def openLog(self):
        if self.ui.log.isVisible() == True:
            self.resize(self.mysize.width(),213)
            self.ui.log.hide()
        else:
            self.resize(self.mysize.width(),389)
            self.ui.log.show()

    def openSetDialog(self):
        #i need to explain this??
        window = QDialog()
        ui = SettingDialog()
        ui.setupUi(window)
        ui.exec_()

    def openInfo(self):
        QMessageBox.about(self.window(), "About Plessc","Plessc " + self.version + " <br><br>Software made by <a href='http://www.mte90.net'><b>Mte90</b></a><br><br><a href='https://github.com/Mte90/Plessc'>Official Site</a>")

    #http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    def sizeof_fmt(self,file_):
        num = os.path.getsize(str(file_))
        for x in ['bytes','KB','MB','GB','TB']:
            if num < 1024.0:
                return str("%3.1f %s") % (num, x)
            num /= 1024.0

    def replace_all(self,text):
        text = text.replace('[39m', '<br>').replace('[31m', '').replace('[22m', '').replace('[0m', '')
        text = text.replace('[90m', '').replace('[27m', '').replace('[7m', '').replace('[1m', '')
        if text == '':
            text = 'OK!'
        return text.lstrip()

def main():
    app = QApplication(sys.argv)
    MainWindow_ = QMainWindow()
    ui = MainWindow()
    ui.setupUi(MainWindow_)
    sys.exit(app.exec_())

main()