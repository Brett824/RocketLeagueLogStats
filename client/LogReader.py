from datetime import datetime, timedelta
import re
import json
import os
import glob
import argparse


def calculateTime(start_time, delta):
    seconds, centiseconds = [int(x) for x in delta.split(".")]
    return start_time + timedelta(seconds=seconds, microseconds=centiseconds*10000)


def readLog(data):
    """BULK OF THE WORK -- RETURNS A LIST OF GAMES PLAYED WITH SKILL GAINS/LOSSES """
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
    return json.dumps([match for log in logs for match in readLog(log)])


def getLogs(path=None):
    path = path or os.environ.get('USERPROFILE', '') + '/Documents/My Games/Rocket League/TAGame/Logs/'
    logs = []
    for fn in glob.glob(path + "*.log"):
        with open(fn, 'r') as f:
            logs.append(f.read())
    return logs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read your Rocket League logs for post-match stats')
    parser.add_argument('logPath', nargs='?', help='Full filepath to the logs')
    args = parser.parse_args()
    print readLogs(getLogs(args.logPath))
