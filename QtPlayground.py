import sys
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PySide6.QtCore import QFile, QDate
from nba_predictor import Ui_MainWindow
import NBAPredictorCheckpoint2GUI
from random import random
from datetime import datetime

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadDateEdit()
        self.loadTable()
        self.loadTeams()

        self.ui.predictButton.clicked.connect(self.predictButtonClick)

    def loadDateEdit(self):
        now = datetime.now()
        self.ui.dateEdit.setDate(QDate(now.year, now.month, now.day))

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
        #self.ui.resultLabel.setText("Home team win chances: .......... . Away team win chances: ..........")
        self.predict(home_shortcut, away_shortcut, day, month, year)

    def predict(self, home, away, day, month, year):
        # self.ui.resultLabel.setText("Home team win chances: " + ".........." + ". Away team win chances: " + "..........")
        
        homeform, awayform = NBAPredictorCheckpoint2GUI.calculate_form(home, away,datetime(year, month, day), self.data)
        self.model, self.data, test_data = NBAPredictorCheckpoint2GUI.git_function('data.txt')

        test_data = {'team_abbreviation_home' : [home], 'team_abbreviation_away' : [away], 'last_5_home_games' : [homeform], 'last_5_away_games' : [awayform]}
        test_data = pd.DataFrame(test_data)
        self.predictions = self.model.predict(input_fn=lambda: NBAPredictorCheckpoint2GUI.predict_input_fn(test_data))

        my_probabilities = []
        for idx, prediction in enumerate(self.predictions):
            my_probabilities.insert(0,prediction)
        self.ui.resultLabel.setText("Home team win chances: " + str(my_probabilities[0]['probabilities'][1]) + ". Away team win chances: " + str(my_probabilities[0]['probabilities'][0]))

    def loadTable(self):
        self.predictions = False
        self.ui.tableWidget.setColumnWidth(0,92)
        self.ui.tableWidget.setColumnWidth(1,92)
        self.ui.tableWidget.setColumnWidth(2,89)
        self.ui.tableWidget.setColumnWidth(3,86)
        self.ui.tableWidget.setColumnWidth(4,86)

        games = [("NYC", "LAL", "10-10-2023", "0.5", "0.5")]
        CSV_TEST_DATA_COLUMN_NAMES = ['team_abbreviation_home', 'team_abbreviation_away', 'Win', 'Loss', 'Date']
        test_data_path = 'data.txt' 
        test_data = pd.read_csv(test_data_path, usecols=CSV_TEST_DATA_COLUMN_NAMES, header=0)
        test_data = test_data.astype({'Win' : 'float32'})
        test_data = test_data.astype({'Loss' : 'float32'})
        model, self.data, test_data = NBAPredictorCheckpoint2GUI.git_function(test_data_path)##
        self.model = model
        predictions = model.predict(input_fn=lambda: NBAPredictorCheckpoint2GUI.predict_input_fn(test_data))
        


        my_probabilities = []
        row_counter = 0
        for idx, prediction in enumerate(predictions):
            row_counter+=1
            my_probabilities.append(prediction)
        self.ui.tableWidget.setRowCount(row_counter)


        for ix in range(0, row_counter):
            self.ui.tableWidget.setItem(ix, 0, QTableWidgetItem("         " + test_data['team_abbreviation_home'][ix]))
            self.ui.tableWidget.setItem(ix, 1, QTableWidgetItem("         " + test_data['team_abbreviation_away'][ix]))
            self.ui.tableWidget.setItem(ix, 2, QTableWidgetItem("  " + str(test_data['Date'][ix])[0:10]))
            self.ui.tableWidget.setItem(ix, 3, QTableWidgetItem(str(my_probabilities[ix]['probabilities'][1])))
            self.ui.tableWidget.setItem(ix, 4, QTableWidgetItem(str(my_probabilities[ix]['probabilities'][0])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())