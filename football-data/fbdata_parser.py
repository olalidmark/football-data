# coding=UTF-8
__author__ = 'fantomen'
import csv
from difflib import SequenceMatcher
import urllib
import datetime
import numpy as np


class fb_data_parser:
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
        'Preston North End': 'Preston'
    }

    LEAGUES = {
        'http://www.football-data.co.uk/mmz4281/1415/E0.csv',
        'http://www.football-data.co.uk/mmz4281/1314/E0.csv',
        'http://www.football-data.co.uk/mmz4281/1415/E1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/E1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/I1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/I1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/SP1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/SP1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/D1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/D1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/F1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/F1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/N1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/N1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/SC0.csv',
        'http://www.football-data.co.uk/mmz4281/1314/SC0.csv',
        'http://www.football-data.co.uk/mmz4281/1415/G1.csv',
        'http://www.football-data.co.uk/mmz4281/1314/G1.csv',
        'http://www.football-data.co.uk/mmz4281/1415/E2.csv',
        'http://www.football-data.co.uk/mmz4281/1314/E2.csv'

    }

    games = []

    def parse_date(self, d):
        d['Date'] = datetime.datetime.strptime(d['Date'], "%d/%m/%y").date()
        return d

    def __init__(self):
        self.games = []
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
            SequenceMatcher(None, home_team_name, g['HomeTeam']).ratio() > 0.6 or SequenceMatcher(None,
                                                                                                  visiting_team_name, g[
                    'AwayTeam']).ratio() > 0.6), self.games)[0]
        except IndexError:
            print "could not find game %s - %s at %s" % ( home_team_name, visiting_team_name, game_date)
        return game


    def get_field(self, team_name, row, field, place):
        r = None
        if row["HomeTeam"] == team_name:
            if place == "away": return
            key = "H" + field
        else:
            if place == "home": return
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


    def get_historical_data_for_team(self, team_name, from_date, field="S", place="both", depth=10):
        """Get historic data of a single field for a team starting at a certain date. Available fields are described here: http://www.football-data.co.uk/notes.txt
        :param team_name: Name of team
        :param from_date: Date as datetime
        :param place; wether to include home, away games or both
        :param field: Which field to return, Ie S for shots or ST for shots on target
        :param depth: How many games to return history for
        :returns List with the field in reversed order, Newest last.
        """
        try:
            games = map(lambda fg: self.get_field(team_name, fg, field, place), sorted(filter(
                lambda g: g['Date'] < from_date and (
                SequenceMatcher(None, team_name, g['HomeTeam']).ratio() > 0.6 or SequenceMatcher(None, team_name, g[
                    'AwayTeam']).ratio() > 0.6), self.games), key=lambda g: g["Date"], reverse=True)[:int(depth * 2.5)])
        except IndexError:
            print "could not find games for %s from %s" % ( team_name, from_date)
        l = list(reversed(filter(None, games)))

        if len(l) >= depth:
            return l[-depth:]
        else:
            a = np.zeros(depth, dtype=np.int)
            a = np.insert(l, 0, a).tolist()
            return a[-depth:]


if __name__ == '__main__':
    # Example usage:
    with fb_data_parser() as parser:
        print parser.get_stats_for_game("Liverpool", "AstonVilla",
                                        datetime.datetime.strptime("2014-09-13", "%Y-%m-%d").date())
        print parser.get_historical_data_for_team("Liverpool",
                                                  datetime.datetime.strptime("2014-12-13", "%Y-%m-%d").date())
