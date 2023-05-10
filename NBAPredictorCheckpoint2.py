import tensorflow as tf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

#IMO JESZCZE SPORO MOZNA POPRAWIC W MODELU, ALE TROCHE NIE MAM POMYSLU CO, GENERALNIE ZOSTALO TYLKO MANIPULOWANIE KOLUMNAMI, BO WSZYSTKIE INNE NARZEDZIA CHYBA SA


CSV_COLUMN_NAMES = ['team_abbreviation_home', 'team_abbreviation_away', 'wl_home', 'game_date']
CSV_RESULTS = ['L', 'W']
train_data_path = 'game.csv'

CSV_TEST_DATA_COLUMN_NAMES = ['team_abbreviation_home', 'team_abbreviation_away', 'Win', 'Loss', 'Date']

test_data_path = 'scraping_script\data.txt' 

data = pd.read_csv(train_data_path, usecols=CSV_COLUMN_NAMES, header=0)

data.dropna(inplace=True)



def filter_last_n_years(df, n):

    n_years_ago = datetime.now() - timedelta(days=365 * n)
    
    if not pd.api.types.is_datetime64_dtype(df['game_date']):
        df['game_date'] = pd.to_datetime(df['game_date'])
    
    filtered_df = df[df['game_date'] > n_years_ago]
    
    return filtered_df

data = filter_last_n_years(data, 10)

data.loc[data['wl_home'] == 'L', 'wl_home'] = 0
data.loc[data['wl_home'] == 'W', 'wl_home'] = 1
# dopytam sie o to Rafalko, ale te kolumny pokroju ilosc rzutow z pola, ilos prob rzucenia za 3, ilosc rzutow osobistych tylko oglupiaja model i zblizaja mi oddsy za bardzo do 50/50, zostalbym przy formie, ewentualnie rozwinal jej wylicznanie, ktore uwzglednia tez jakosc przeciwnika, do pomyslenia
data = data.astype({'team_abbreviation_home': 'string', 'team_abbreviation_away': 'string', 'wl_home': 'int32', 'game_date': 'datetime64[D]'})#, 'fgm_home' : 'float32', 'fgm_away' : 'float32', 'fg3a_home' : 'float32', 'fg3a_away' : 'float32'})

#ile wygranych w 5 ostatnich domowych meczach domowej druzyny
data['last_5_home_games'] = 0
#ile wygranych w 5 ostatnich wyjazdowych meczach druzyny wyjazdowwej
data['last_5_away_games'] = 0





for team in data['team_abbreviation_away'].unique():
    team_mask = data['team_abbreviation_away'] == team
    data.loc[team_mask, 'last_5_away_games'] = 5 - data.loc[team_mask, 'wl_home'].rolling(window=5, min_periods=1).sum() 


for team in data['team_abbreviation_home'].unique():
    team_mask = data['team_abbreviation_home'] == team
    data.loc[team_mask, 'last_5_home_games'] = data.loc[team_mask, 'wl_home'].rolling(window=5, min_periods=1).sum()


data = data.dropna()


#def add_last_10_results(df):
#    teams = df['team_abbreviation_home'].unique()
#    team_form = {}
#    for team in teams:
#        team_form[team] = {'home': [], 'away': []}
    
#        home_form_col = []
#        away_form_col = []
    
#        for i, row in df.iterrows():
#            home_team = row['team_abbreviation_home']
#            away_team = row['team_abbreviation_away']
#            home_win = row['wl_home'] == 1
        
#            if len(team_form[home_team]['home']) < 10:
#                team_form[home_team]['home'].append(home_win)
#            else:
#                team_form[home_team]['home'] = team_form[home_team]['home'][1:] + [home_win]
#            home_form = sum([1 if x else 0 for x in team_form[home_team]['home']])
#            home_form_col.append(home_form)
        
#            if len(team_form[away_team]['away']) < 10:
#                team_form[away_team]['away'].append(not home_win)
#            else:
#                team_form[away_team]['away'] = team_form[away_team]['away'][1:] + [not home_win]
#            away_form = sum([1 if x else 0 for x in team_form[away_team]['away']])
#            away_form_col.append(away_form)
    
#    df['home_team_last_10_results'] = home_form_col
#    df['away_team_last_10_results'] = away_form_col
#    return df

#overall results of home team in the last 10 games (home and away)
# add_last_10_results(data)

# TO NA RAZIE NIE DZIALA, DO DOKONCZENIA - MOZE POPRAWIC MODEL ZNACZACO
#TODO : Generalnie to co jest wyzej mega wolne - zrobic raz, zapisac do tej tabelki game.csv i usunac ten fragment, zeby nie odpalac za kazdym razem
test_data = pd.read_csv(test_data_path, usecols=CSV_TEST_DATA_COLUMN_NAMES, header=0)
test_data = test_data.astype({'Win' : 'float32'})
test_data = test_data.astype({'Loss' : 'float32'})
test_data = test_data.astype({'Date' : 'datetime64[D]'})

    
# test_start_date = test_data['Date'].min() # uzupelnienie test seta o formy z ostatnich 5 meczow
# data_filtered = data[data['game_date'] > test_start_date]

home_team_last_5 = [] 
for index, row in test_data.iterrows():
    home_team = row['team_abbreviation_home']
    home_games = data[data['team_abbreviation_home'] == home_team]
    home_games_last_5 = home_games.tail(5)
    home_team_last_5.append(home_games_last_5['wl_home'].sum())
test_data['last_5_home_games'] = home_team_last_5

away_team_last_5 = []
for index, row in test_data.iterrows():
    away_team = row['team_abbreviation_away']
    away_games = data[data['team_abbreviation_away'] == away_team]
    away_games_last_5 = away_games.tail(5)
    away_team_last_5.append(5 - away_games_last_5['wl_home'].sum())
test_data['last_5_away_games'] = away_team_last_5

test_data = test_data.astype({'last_5_home_games' : 'int32'})
test_data = test_data.astype({'last_5_away_games' : 'int32'})
data = data.drop(['game_date'], axis=1)

train_data = pd.DataFrame(data.sample(frac=0.9, random_state=25))

print(train_data.head())



def calculate_probabilities(test_data):
    total_prob = 1 / ((1/test_data['Win']) + (1/test_data['Loss']))
    win_prob = (1/test_data['Win']) * total_prob
    loss_prob = (1/test_data['Loss']) * total_prob
    return pd.DataFrame({'Win': win_prob, 'Loss': loss_prob})

win_loss_data = calculate_probabilities(test_data)

test_data['Win'] = win_loss_data['Win']
test_data['Loss'] = win_loss_data['Loss']


print(test_data)

print(f'Training data size: {train_data.shape[0]}')
print(f'Testing data size: {test_data.shape[0]}')


feature_columns = []
home_team = tf.feature_column.categorical_column_with_vocabulary_list(
      'team_abbreviation_home', data['team_abbreviation_home'].unique())

away_team = tf.feature_column.categorical_column_with_vocabulary_list(
      'team_abbreviation_away', data['team_abbreviation_away'].unique())

feature_columns.append(tf.feature_column.indicator_column(home_team))
feature_columns.append(tf.feature_column.indicator_column(away_team))
feature_columns.append(tf.feature_column.numeric_column('last_5_home_games'))
feature_columns.append(tf.feature_column.numeric_column('last_5_away_games'))
# feature_columns.append(tf.feature_column.numeric_column('fgm_home'))
# feature_columns.append(tf.feature_column.numeric_column('fgm_away'))
# feature_columns.append(tf.feature_column.numeric_column('fg3a_home'))
# feature_columns.append(tf.feature_column.numeric_column('fg3a_away'))

# train_data = pd.DataFrame(data.sample(frac=0.8, random_state=25))
eval_data = pd.DataFrame(data.drop(train_data.index))

def make_input_fn(data_df, label_df, num_epochs=10, shuffle=True, batch_size=32):
    def input_function():
        ds = tf.data.Dataset.from_tensor_slices((dict(data_df), label_df))
        if shuffle:
            ds = ds.shuffle(1000)
        ds = ds.batch(batch_size).repeat(num_epochs)
        return ds
    return input_function

y_train = train_data.pop('wl_home')
y_eval = eval_data.pop('wl_home')

train_input_fn = make_input_fn(train_data, y_train)
eval_input_fn = make_input_fn(eval_data, y_eval, num_epochs=1, shuffle=False)

model = tf.estimator.DNNClassifier(
    feature_columns=feature_columns,
    hidden_units=[16, 16],
    n_classes=2)

model.train(input_fn=train_input_fn, steps=1000)

eval_result = model.evaluate(input_fn=eval_input_fn)

print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**eval_result))

def predict_input_fn(df, batch_size = 32):
    selected_columns = ['team_abbreviation_home', 'team_abbreviation_away', 'last_5_home_games', 'last_5_away_games']
    features = df[selected_columns].to_dict(orient='list')
    dataset = tf.data.Dataset.from_tensor_slices(features)
    dataset = dataset.batch(batch_size)
    return dataset

predictions = model.predict(input_fn=lambda: predict_input_fn(test_data))

mean_error = 0 # sposob oceny jakosci rozwiazania

for idx, prediction in enumerate(predictions):

    home_win_odds = prediction['probabilities'][1]
    away_win_odds = prediction['probabilities'][0]
    mean_error += abs(test_data['Win'].iloc[idx] - home_win_odds)
    print('Prediction {} home team win odds: {:.2f}     away team win odds: {:.2f} '.format(idx+1, home_win_odds, away_win_odds))

mean_error /= len(test_data)
print('Mean error is {:.2f}\n'.format(mean_error))
print('\n Here are the actual odds from a betting site')
test_data_to_print = test_data[['team_abbreviation_home','team_abbreviation_away', 'Win', 'Loss']]
print (test_data_to_print)
