# coding=UTF-8
__author__ = 'fantomen'
import csv
from difflib import SequenceMatcher
import urllib
import datetime
import numpy as np


class fbDataParser:

    LEAGUES = [
        'http://www.football-data.co.uk/mmz4281/1718/E0.csv',
        'http://www.football-data.co.uk/mmz4281/1718/E1.csv',
        'http://www.football-data.co.uk/mmz4281/1718/I1.csv',
        'http://www.football-data.co.uk/mmz4281/1718/SP1.csv',
        'http://www.football-data.co.uk/mmz4281/1718/D1.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Allsvenskan2017.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Superettan2017.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/tippeligaen2017.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/Veikkausliiga2017.csv',
        'https://s3-eu-west-1.amazonaws.com/tipset/danska-superligan2017.csv'
    ]

    games = []

    def parse_date(self, d):
        try:
            d['Date'] = datetime.datetime.strptime(d['Date'], "%d/%m/%y").date()
        except ValueError:
            d['Date'] = datetime.datetime.strptime("01/01/70", "%d/%m/%y").date()
        return d

    def read_urls(self, urls):
        for u in urls:
            try:
                url = u
            except KeyError:
                self.games = []
                continue
            remote_file = urllib.urlopen(url)
            reader = csv.DictReader(remote_file.readlines())
            self.games += reader

    def __init__(self, url=None, urls=None, silent=False):
        self.silent = silent
        self.games = []
        if url:
            remote_file = urllib.urlopen(url)
            reader = csv.DictReader(remote_file.readlines())
            self.games = reader
        elif urls:
            self.read_urls(urls)
        else:
            self.read_urls(self.LEAGUES)

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
        except IndexError, ValueError:
            print "could not find game %s - %s at %s" % (home_team_name, visiting_team_name, game_date)
        return game

    def get_field(self, team_name, row, field, place, inverse):
        r = None

        if SequenceMatcher(None, team_name, row["HomeTeam"]).ratio() > 0.8:
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
            if not self.silent:
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
            print "could not find games for %s from %s" % (team_name, from_date)
        l = list(reversed([x for x in games if x is not None]))

        ret = []

        if len(l) >= depth:
            ret = l[-depth:]
        else:
            a = np.zeros(depth, dtype=np.int)
            a = np.insert(l, 0, a).tolist()
            ret = a[-depth:]

        if ret.count(0) > depth / 2:
            if not self.silent:
                print "WARNING: Data may not have been found for: " + team_name
        return ret


if __name__ == '__main__':
    # Example usage:
    with fbDataParser() as parser:
        #print parser.get_stats_for_game("Liverpool", "AstonVilla",
        #                                datetime.datetime.strptime("2014-09-13", "%Y-%m-%d").date())
        print parser.get_historical_data_for_team("Bröndby IF",
                                                  datetime.datetime.strptime("2017-09-01", "%Y-%m-%d").date(), depth=20)

        print parser.get_historical_data_for_team("Arsenal",
                                                  datetime.datetime.strptime("2017-09-01", "%Y-%m-%d").date(),
                                                  inverse=True, depth=3)