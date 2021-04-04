from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit, 
                                QVBoxLayout, QComboBox, QWidget, QProgressBar)
from PyQt5.QtCore import QProcess
from PyQt5 import QtGui #ICONE

import sys
import re, os

# A regular expression, to extract the % complete.
progress_re = re.compile("Total complete: (\d+)%")

def simple_percent_parser(output):
    """
    Matches lines using the progress_re regex, 
    returning a single integer for the % progress.
    """
    m = progress_re.search(output)
    if m:
        pc_complete = m.group(1)
        return int(pc_complete)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.p = None
        

        scriptDir = os.path.dirname(os.path.realpath(__file__))

        self.setWindowTitle("Desgfragmentador de discos.. v1.2")        
        
        self.setMinimumWidth(640)
        self.setMinimumHeight(480)

        #CRIAR gui
        self.btn = QPushButton("Desfragmentar")
        self.btn.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'icon.png'))
        self.btn.pressed.connect(self.start_process) #ao pressionar self.start_process
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.combo = QComboBox() #criando combo combo.addItem("lbl")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        self.combo.clear()
        self.combo.addItem('1. /dev/sda1') #
        self.combo.addItem('2. /dev/sda2') #
        self.combo.addItem('3. /dev/sda3') #
        self.combo.addItem('4.  /dev/sdb')

        l = QVBoxLayout() #percursor do layout QVBOX
        l.addWidget(self.btn) #botao

        #mostrar
        l.addWidget(self.combo) #combo
        l.addWidget(self.text) #texto
        l.addWidget(self.progress) #status
        
        w = QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)
    def comboadd(add):
        self.combo.addItem(add)


    def message(self, s):
        self.text.appendPlainText(s)

    def start_process(self):
        #função para buscar partições
        
        if self.p is None:  # No process running.
            self.message("*** Gerando LOG ***")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            partition = self.combo.currentIndex()
            if partition == 0:
                self.p.start("e4defrag", ['/dev/sda1'])
            elif partition == 1:
                self.p.start("e4defrag", ['/dev/sda2']) #desfragmentar
            elif partition == 2:
                self.p.start("e4defrag", ['/dev/sda3'])
            elif partition == 3:
                self.p.start("e4defrag", ['/dev/sdb'])
            
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        # Extract progress if it is in the data.
        progress = simple_percent_parser(stderr)
        if progress:
            self.progress.setValue(progress)
        self.message(stderr)

    def handle_stdout(self): #escrever mensagem
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        #barra de progresso

        progress = simple_percent_parser(stdout)
        print(progress)
        if progress:
            self.progress.setValue(progress)
        self.message(stdout)

    def handle_state(self, state):
        states = {   
            QProcess.NotRunning: 'Não foi possivel executar',
            QProcess.Starting: 'Iniciando',
            QProcess.Running: 'Rodando',
        }
        state_name = states[state]
        self.message(f"*** {state_name} ***")

    def process_finished(self):
        self.message("Finalizado.")
        self.p = None        


app = QApplication(sys.argv)

w = MainWindow()

w.show()

app.exec_()
