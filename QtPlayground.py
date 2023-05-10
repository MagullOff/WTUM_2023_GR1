import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PySide6.QtCore import QFile
from nba_predictor import Ui_MainWindow

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadTable()
        self.loadTeams()

        self.ui.predictButton.clicked.connect(self.predictButtonClick)

    def loadTeams(self):
        self.full_to_short = {}
        teams_file = open("teams.txt", "r")
        for team in teams_file.readlines():
            line=team.split(';')
            self.ui.homeTeamComboBox.addItem(line[0])
            self.ui.awayTeamComboBox.addItem(line[0])
            self.full_to_short[line[0]]=line[1][0:-2]
        teams_file.close()

    def predictButtonClick(self):
        home_shortcut = self.full_to_short[self.ui.homeTeamComboBox.currentText()]
        away_shortcut = self.full_to_short[self.ui.awayTeamComboBox.currentText()]
        year = self.ui.dateEdit.date().year()
        month = self.ui.dateEdit.date().month()
        day = self.ui.dateEdit.date().day()
        self.predict(home_shortcut, away_shortcut, day, month, year)

    def predict(self, home, away, day, month, year):
        home_win = 0.7
        away_win = 0.3
        self.ui.resultLabel.setText("Home team win chances: " + str(home_win) + ". Away team win chances: " + str(away_win))

    def loadTable(self):
        self.ui.tableWidget.setColumnWidth(0,92)
        self.ui.tableWidget.setColumnWidth(1,92)
        self.ui.tableWidget.setColumnWidth(2,89)
        self.ui.tableWidget.setColumnWidth(3,86)
        self.ui.tableWidget.setColumnWidth(4,86)

        games = [("NYC", "LAL", "10-10-2023", "0.5", "0.5")]
        self.ui.tableWidget.setRowCount(len(games))
        row = 0
        for game in games:
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(game[0]))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(game[1]))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(game[2]))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(game[3]))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(game[4]))
            row+=1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())