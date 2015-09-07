# coding=UTF-8
__author__ = 'fantomen'
import csv
from difflib import SequenceMatcher
import urllib
import datetime
import numpy as np


class fbDataParser:
    NAMES = {
        'Manchester United': 'Man United',
        'Manchester City': 'Man City',
        'Queens PR': 'QPR',
        'West Bromwich': 'West Brom',
        'Oldham Athletic': 'Oldham',
        'Bayern München': 'Bayern Munich',
        'Borussia Mönchengladbach': 'M\'gladbach',
        'Crewe Alexandra': 'Crewe',
        'Fleetwood': 'Fleetwood Town',
        'Preston North End': 'Preston',
        'Queens Park Rangers': 'QPR',
        'Wolverhampton': 'Wolves',
        'Yeovil Town': 'Yeovil',
        'Nottingham Forest': 'Nott\'m Forest',
        'Athletic Bilbao': 'Ath Bilbao',
        'Sporting Gijon': 'Sp Gijon',
        'Real Sociedad': 'Sociedad',
        'Deportivo La Coruna': 'La Coruna',
        'Atletico de Madrid': 'Ath Madrid',
        'Rayo Vallecano': 'Vallecano',
        'Celta Vigo': 'Celta',
        'Bayer Leverkusen': 'Leverkusen',
        '1899 Hoffenheim': 'Hoffenheim',
        'Hamburger SV': 'Hamburg',
        'Djurgårdens IF': 'Djurgården',
        'Assyriska Föreningen': 'Assyriska',
        'Örebro SK': 'Örebro',
        'Real Betis': 'Betis',
        'Racing Santander': 'Santander',
        'Borussia Dortmund': 'Dortmund',
        'Hertha Berlin': 'Hertha',
        'FSV Mainz': 'Mainz',
        'FC Nürnberg': 'Nürnberg',
        'Eintracht Braunschweig': 'Braunschweig',
        'Olympique Marseille': 'Marseille',
        'FC Metz': 'Metz',
        'VfL Bochum': 'Bochum',
        'Glasgow Rangers': 'Rangers',
        'Partick Thistle': 'Partick',
        'Energie Cottbus': 'Cottbus',
        'Arminia Bielefeld': 'Bielefeld',
        'FC St. Pauli': 'St Pauli',
        'Dundee FC': 'Dundee',
        'Jönköpings Södra IF': 'Jönköpings Södra'
    }

    LEAGUES = {
        'http://www.football-data.co.uk/mmz4281/1516/E0.csv',
        'http://www.football-data.co.uk/mmz4281/1415/E0.csv',
        'http://www.football-data.co.uk/mmz4281/1314/E0.csv',
        'http://www.football-data.co.uk/mmz4281/1516/E1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/E1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/E1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/I1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/I1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/I1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/SP1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/SP1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/SP1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/D1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/D1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/D1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/F1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/F1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/F1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/N1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/N1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/N1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/SC0.csv',
        'http://www.football-data.co.uk/mmz4281/1415/SC0.csv',
        'http://www.football-data.co.uk/mmz4281/1314/SC0.csv',
        'http://www.football-data.co.uk/mmz4281/1516/G1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/G1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/G1.csv',
        'http://www.football-data.co.uk/mmz4281/1516/E2.csv',
        'http://www.football-data.co.uk/mmz4281/1415/E2.csv',
        'http://www.football-data.co.uk/mmz4281/1314/E2.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Allsvenskan2014.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Allsvenskan2015.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Superettan2014.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Superettan2015.csv'

    }

    games = []

    def parse_date(self, d):
        d['Date'] = datetime.datetime.strptime(d['Date'], "%d/%m/%y").date()
        return d

    def __init__(self, url=None):
        self.games = []
        if url:
            remote_file = urllib.urlopen(url)
            reader = csv.DictReader(remote_file.readlines())
            self.games = reader
        else:
            for l in self.LEAGUES:
                try:
                    url = l
                except KeyError:
                    self.games = []
                    continue
                remote_file = urllib.urlopen(url)
                reader = csv.DictReader(remote_file.readlines())
                self.games += reader

        self.games = map(lambda g: self.parse_date(g), self.games)

        print "parsed %s games" % len(self.games)

    def __del__(self):
        self.games = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.games = None

    def __enter__(self):
        return self

    def get_stats_for_game(self, home_team_name, visiting_team_name, game_date):
        """Get full stats row for a single game. The stats returned are described here: http://www.football-data.co.uk/notes.txt
        :param home_team_name: Name of home team
        :param visiting_team_name: Name of away team
        :param game_date: Date of the game as datetime
        :returns Game stats as Dict
        """
        game = []
        try:
            game = filter(lambda g: g['Date'] == game_date and (
                SequenceMatcher(None, home_team_name, g['HomeTeam']).ratio() > 0.8 or SequenceMatcher(None,
                                                                                                      visiting_team_name,
                                                                                                      g[
                                                                                                          'AwayTeam']).ratio() > 0.8),
                          self.games)[0]
        except IndexError:
            print "could not find game %s - %s at %s" % ( home_team_name, visiting_team_name, game_date)
        return game


    def get_field(self, team_name, row, field, place, inverse):
        r = None

        if row["HomeTeam"] == team_name:
            if place == "away": return
            if inverse:
                key = "A" + field
            else:
                key = "H" + field
        else:
            if place == "home": return
            if inverse:
                key = "H" + field
            else:
                key = "A" + field

        try:
            r = row[key]
        except KeyError:
            print "could not find key %s for %s" % (key, team_name)
            r = 0
        try:
            r = int(r)
        except ValueError:
            r = 0
        return r


    def get_historical_data_for_team(self, team_name, from_date, field="S", place="both", depth=10, inverse=False):
        """Get historic data of a single field for a team starting at a certain date. Available fields are described here: http://www.football-data.co.uk/notes.txt
        :param team_name: Name of team
        :param from_date: Date as datetime
        :param place; wether to include home, away games or both
        :param field: Which field to return, Ie S for shots or ST for shots on target
        :param depth: How many games to return history for
        :param inverse: Get opposing stats instead
        :returns List with the field in reversed order, Newest last.
        """
        try:
            games = map(lambda fg: self.get_field(team_name, fg, field, place, inverse), sorted(filter(
                lambda g: g['Date'] < from_date and (
                    SequenceMatcher(None, team_name, g['HomeTeam']).ratio() > 0.8 or SequenceMatcher(None, team_name, g[
                        'AwayTeam']).ratio() > 0.8), self.games), key=lambda g: g["Date"], reverse=True)[
                                                                                         :int(depth * 2.5)])
        except IndexError:
            print "could not find games for %s from %s" % ( team_name, from_date)
        l = list(reversed([x for x in games if x is not None]))

        ret = []

        if len(l) >= depth:
            ret = l[-depth:]
        else:
            a = np.zeros(depth, dtype=np.int)
            a = np.insert(l, 0, a).tolist()
            ret = a[-depth:]

        if ret.count(0) > depth / 2:
            print "WARNING: Data may not have been found for: " + team_name.encode("UTF-8")

        return ret


if __name__ == '__main__':
    # Example usage:
    with fbDataParser() as parser:
        print parser.get_stats_for_game("Liverpool", "AstonVilla",
                                        datetime.datetime.strptime("2014-09-13", "%Y-%m-%d").date())
        print parser.get_historical_data_for_team("Chelsea",
                                                  datetime.datetime.strptime("2015-09-07", "%Y-%m-%d").date(),
                                                  inverse=True)
