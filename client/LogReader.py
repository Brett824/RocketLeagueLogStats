
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import json
import os
import glob


def calculateTime(start_time, delta):
    seconds, centiseconds = [int(x) for x in delta.split(".")]
    return start_time + relativedelta(seconds=seconds, microseconds=centiseconds*10000)


def readLog(data):
    """BULK OF THE WORK -- RETURNS A JSON OF GAMES PLAYED WITH SKILL GAINS/LOSSES """
    data = data.splitlines()
    start_time = datetime.strptime(data[0], 'Log: Log file open, %m/%d/%y %H:%M:%S')
    matches = []
    for line in data:
        if 'ClientSetSkill' in line:
            search = re.search("\[(.*)\].*Playlist=(.*?) Mu=(.*?) Sigma=(.*?) DeltaRankPoints=(.*?) RankPoints=(.*)", line)
            time, playlist, mu, sigma, delta, rp = [search.group(x) for x in [1, 2, 3, 4, 5, 6]]
            time = calculateTime(start_time, time)
            matches.append({
                'time': time.isoformat(),
                'playlist': playlist,
                'delta': int(delta),
                'hidden_skill': float(mu) - (3 * float(min(sigma, 2.5))),
                'rank': int(rp) + int(delta)
            })
    return matches


def readLogs(logs):
    return json.dumps([matches for log in logs for matches in readLog(log)])


def loadLogs(path=None):
    path = path or os.environ['USERPROFILE'] + '/Documents/My Games/Rocket League/TAGame/Logs/'
    logs = []
    for fn in glob.glob(path + "*.log"):
        with open(fn, 'r') as f:
            logs.append(f.read())
    return logs
