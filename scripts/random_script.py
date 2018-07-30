#!/usr/bin/env python

import csv
import random

csv_file_locs = [
    "../csv/goalkeepers.csv",
    "../csv/defenders.csv",
    "../csv/midfielders.csv",
    "../csv/forwards.csv",
]

number_players = [
    2,5,5,3
]

scores = []

for i in range(60000):
    player_counts = []
    readers = []
    team = []
    total_score = 0
    total_cost = 0
    final_team = []

    for i in range(len(csv_file_locs)):
        with open(csv_file_locs[i], newline='') as csvfile:
            dict_length = 0
            reader = csv.DictReader(csvfile)
            for row in reader:
                dict_length += 1
            player_counts.append(dict_length)
            team.append(random.sample(range(player_counts[i]), number_players[i]))

    for i in range(len(csv_file_locs)):
        with open(csv_file_locs[i], newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                id = int(row["id"])
                if id in team[i]:
                    final_team.append(row["player"])
                    total_cost += float(row["cost"])
                    total_score += int(row["pts"])

    scores.append([total_score,total_cost, final_team])

no_overs = []

for i in range(len(scores)):
    if scores[i][1] <= 100:
        no_overs.append(scores[i])

sorted_list = sorted(no_overs)
top_score = sorted_list[-1]
print(top_score[0])
print(top_score[1])
for i in range(len(top_score[2])):
    print(top_score[2][i])
