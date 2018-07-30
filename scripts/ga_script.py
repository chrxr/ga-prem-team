#!/usr/bin/env python

import csv
import random
import copy
import sys

def dedupe(seed,num_players, player_amount):
    seed = set(seed)
    if len(seed) < player_amount:
        seed = random.sample(range(num_players), player_amount)
        dedupe(seed, num_players, player_amount)
    return seed

def get_players(all_players, index, player_amount):
    players = []
    player_ids = []
    num_players = len(all_players[index])
    seed = random.sample(range(num_players), player_amount)
    seed = dedupe(seed, num_players, player_amount)
    for num in seed:
        players.append(copy.deepcopy(all_players[index][num]))
        player_ids.append(players[-1]["id"])
    return [sorted(players, key=lambda k: k["id"]), player_ids]

class Team:
    def __init__(self):
        self.goalkeepers = []
        self.goal_ids =[]
        self.defenders = []
        self.def_ids = []
        self.midfielders = []
        self.mid_ids = []
        self.forwards = []
        self.for_ids = []
        self.cost = 0
        self.score = 0
        self.value = 0
        self.full_team = []
        self.generation = 0

    def create_team(self, all_players, generation):
        self.goalkeepers, self.goal_ids = get_players(all_players, 0, 2)
        self.defenders, self.def_ids = get_players(all_players, 1, 5)
        self.midfielders, self.mid_ids = get_players(all_players, 2, 5)
        self.forwards, self.for_ids = get_players(all_players, 3, 3)
        self.full_team = self.goalkeepers + self.defenders + self.midfielders + self.forwards
        self.generation = generation

    def update_ids(self):
        self.goal_ids = []
        self.def_ids = []
        self.mid_ids = []
        self.for_ids = []
        for player in self.goalkeepers:
            self.goal_ids.append(player["id"])
        for player in self.midfielders:
            self.mid_ids.append(player["id"])
        for player in self.defenders:
            self.def_ids.append(player["id"])
        for player in self.forwards:
            self.for_ids.append(player["id"])


    def get_cost_value_score(self):
        self.cost = 0
        self.score = 0
        self.value = 0
        for i in range(len(self.full_team)):
            self.cost += self.full_team[i]["cost"]
            self.score += self.full_team[i]["score"]
        if self.cost > 100:
            self.value = self.score - (self.cost-100)*125
        else:
            self.value = self.score

class Population:
    def __init__(self, size, death_rate=0.5, mut_rate=0.2, min_size=0.5):
        self.teams = []
        self.size = size
        self.death_rate = death_rate
        self.mut_rate = mut_rate
        self.min_size = 0.5


    def fill_population(self, all_players, generation):

        if len(self.teams) < (self.size*self.min_size) and len(self.teams) > 0:
            for i in range(self.size-len(self.teams)):
                team = Team()
                team.create_team(all_players, generation)
                team.get_cost_value_score()
                self.teams.append(team)
        elif len(self.teams) < 1:
            for i in range(self.size):
                team = Team()
                team.create_team(all_players, generation)
                team.get_cost_value_score()
                self.teams.append(team)


    def mate(self):
        for i in range(1, len(self.teams), 2):

            goalie_index = random_numbers(2,1)
            def_index = random_numbers(5,2)
            mid_index = random_numbers(5,2)
            for_index = random_numbers(3,1)
        
            if self.teams[i].goalkeepers[goalie_index[0]]["id"] not in self.teams[i-1].goal_ids and self.teams[i-1].goalkeepers[goalie_index[0]]["id"] not in self.teams[i].goal_ids:
                swap = copy.deepcopy(self.teams[i].goalkeepers[goalie_index[0]])
                self.teams[i].goalkeepers[goalie_index[0]] = self.teams[i-1].goalkeepers[goalie_index[0]]
                self.teams[i-1].goalkeepers[goalie_index[0]] = swap
                self.teams[i].update_ids()
            
            for x in def_index:
                if self.teams[i].defenders[x]["id"] not in self.teams[i-1].def_ids and self.teams[i-1].defenders[x]["id"] not in self.teams[i].def_ids:
                    swap = self.teams[i].defenders[x]
                    self.teams[i].defenders[x] = self.teams[i-1].defenders[x]
                    self.teams[i-1].defenders[x] = swap
            
            for x in mid_index:
                if int(self.teams[i].midfielders[x]["id"]) not in self.teams[i-1].mid_ids and self.teams[i-1].midfielders[x]["id"] not in self.teams[i].mid_ids:
                    swap = self.teams[i].midfielders[x]
                    self.teams[i].midfielders[x] = self.teams[i-1].midfielders[x]
                    self.teams[i-1].midfielders[x] = swap

            for x in for_index:
                if int(self.teams[i].forwards[x]["id"]) not in self.teams[i-1].for_ids and self.teams[i-1].forwards[x]["id"] not in self.teams[i].for_ids:
                    swap = self.teams[i].forwards[x]
                    self.teams[i].forwards[x] = self.teams[i-1].forwards[x]
                    self.teams[i-1].forwards[x] = swap

            self.teams[i].full_team = self.teams[i].goalkeepers + self.teams[i].defenders + self.teams[i].midfielders + self.teams[i].forwards
            self.teams[i-1].full_team = self.teams[i-1].goalkeepers + self.teams[i-1].defenders + self.teams[i-1].midfielders + self.teams[i-1].forwards
            
            self.teams[i].get_cost_value_score()
            self.teams[i-1].get_cost_value_score()

            self.teams[i].update_ids()
            self.teams[i-1].update_ids()
            
    def kill(self):
        self.teams = sorted(self.teams, key=lambda k: k.value)
        kill_number = round(len(self.teams) * self.death_rate + 1) * -1
        del self.teams[0:kill_number]

    def mutate(self, all_players):
        mutate_index = random_numbers(len(self.teams), round(len(self.teams)*self.mut_rate))
        for i in mutate_index:
            seed = random.randrange(1,15)
            if seed < 3:
                x = random.randrange(0, len(all_players[0]))
                random_goalie = all_players[0][x].copy()
                goalie_index = random_numbers(2,1)
                if random_goalie["id"] not in self.teams[i].goal_ids:
                    self.teams[i].goalkeepers[goalie_index[0]] = random_goalie

            elif seed < 9:
                x = random.randrange(0, len(all_players[1]))
                random_def = all_players[1][x].copy()
                def_index = random_numbers(5,1)
                if int(random_def["id"]) not in self.teams[i].def_ids:
                    self.teams[i].defenders[def_index[0]] = random_def

            elif seed < 14:
                x = random.randrange(0, len(all_players[2]))
                random_mid = all_players[2][x].copy()
                mid_index = random_numbers(5,1)
                if int(random_mid["id"]) not in self.teams[i].mid_ids:
                    self.teams[i].midfielders[mid_index[0]] = random_mid

            else:
                x = random.randrange(0, len(all_players[3]))
                random_for = all_players[3][x].copy()
                for_index = random_numbers(3,1)
                if int(random_for["id"]) not in self.teams[i].for_ids:
                    self.teams[i].forwards[for_index[0]] = random_for

            self.teams[i].get_cost_value_score()
            self.teams[i].update_ids()

            
def read_files():
    csv_file_locs = [
        "../csv/goalkeepers.csv",
        "../csv/defenders.csv",
        "../csv/midfielders.csv",
        "../csv/forwards.csv",
    ]
    all_players = []
    for i in range(len(csv_file_locs)):
        with open(csv_file_locs[i], newline='') as csvfile:
            dict_length = 0
            reader = csv.DictReader(csvfile)
            players = []
            for index, row in enumerate(reader):
                player = {
                    "id": index,
                    "name":row["player"],
                    "score": int(row["pts"]),
                    "cost": float(row["cost"]),
                }
                players.append(player)
            all_players.append(players)
    return all_players

def random_numbers(num_range, amount):
    numbers = random.sample(range(num_range), amount)
    to_set = set(numbers)
    if len(to_set) < len(numbers):
        random_numbers(amount, range)
    return numbers

all_players = read_files()

population = Population(1000)
generation = 0
top_score = 0

for i in range(1000):
    generation += 1
    population.fill_population(all_players, generation)
    population.mutate(all_players)
    population.mate()
    population.kill()

    if population.teams[-1].value > top_score:
        top_score = copy.deepcopy(population.teams[-1].value)
        top_team = copy.deepcopy(population.teams[-1])
        print(top_score)

print("Score: " + str(top_score))
print("Cost: " + str(top_team.cost))

for player in top_team.goalkeepers:
    print(player["name"] + ', ' + str(player["cost"]) + ', ' + str(player["score"]))
for player in top_team.defenders:
    print(player["name"] + ', ' + str(player["cost"]) + ', ' + str(player["score"]))
for player in top_team.midfielders:
    print(player["name"] + ', ' + str(player["cost"]) + ', ' + str(player["score"]))
for player in top_team.forwards:
    print(player["name"] + ', ' + str(player["cost"]) + ', ' + str(player["score"]))

