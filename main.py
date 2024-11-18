from enum import Enum
from itertools import combinations, product
import numpy as np
import pandas as pd


class Player:
    def __init__(self, name):
        self.name = name
        self.lost_hp = 0


class Actions(Enum):
    Shoot_self = 0
    Shoot_opponent = 1


class Round(Enum):
    Blank = 0
    Live = 1


class Log:
    def __init__(self):
        self.first_action = None
        self.p1_lost_hp = 0
        self.p2_lost_hp = 0
        self.next_round = None


def shoot(player, opponent, current_round, action):
    match action:
        case Actions.Shoot_self:
            match current_round:
                case Round.Blank:
                    return player, opponent
                case Round.Live:
                    player.lost_hp -= 1
                    return opponent, player
        case Actions.Shoot_opponent:
            match current_round:
                case Round.Blank:
                    return opponent, player
                case Round.Live:
                    opponent.lost_hp -= 1
                    return opponent, player


def simulation_step(
    current_load, player, opponent, turn_count, action_list, log, live, blanks
):
    if len(current_load) == 0:
        if player.name == "Player 1":
            player1_hp = player.lost_hp
            player2_hp = opponent.lost_hp
        else:
            player2_hp = player.lost_hp
            player1_hp = opponent.lost_hp

        log.p1_lost_hp = player1_hp
        log.p2_lost_hp = player2_hp
        log.next_round = player

        with open("log.csv", "a") as file:
            entry = ",".join(
                [
                    log.first_action.name,
                    str(log.p1_lost_hp),
                    str(log.p2_lost_hp),
                    log.next_round.name + "\n",
                ]
            )
            file.write(entry)

        # with open("log.txt", "a") as file:
        #    for entry in log:
        #        file.write(str(entry) + "\n")
        #    file.write("\n")
        # log = []
        return None

    current_round = Round(current_load.pop(0))
    current_action = Actions(action_list.pop(0))

    if log.first_action is None:
        log.first_action = current_action

    if (live == 0) and (current_action == Actions.Shoot_opponent):
        return None

    if (blanks == 0) and (current_action == Actions.Shoot_self):
        return None

    turn_count += 1

    match current_round:
        case Round.Live:
            live -= 1
        case Round.Blank:
            blanks -= 1

    new_player, new_opponent = shoot(player, opponent, current_round, current_action)

    # if player.name == "Player 1":
    #    player1_hp = player.lost_hp
    #    player2_hp = opponent.lost_hp
    # else:
    #    player2_hp = player.lost_hp
    #    player1_hp = opponent.lost_hp

    # new_log = (
    #    "Turn: {turn}, Shooter: {shooter}, Opponent: {opponent}, Current round: {round}, Action: {action}, Player 1 lost HP: {p1_hp}, Player 2 lost HP: {p2_hp},Next turn: {next}".format(
    #        turn=turn_count,
    #        shooter=player.name,
    #        opponent=opponent.name,
    #        round=current_round.name,
    #        action=current_action.name,
    #        p1_hp=player1_hp,
    #        p2_hp=player2_hp,
    #        next=new_player.name,
    #    ),
    # )
    # log.append(new_log)
    simulation_step(
        current_load=current_load,
        player=new_player,
        opponent=new_opponent,
        turn_count=turn_count,
        action_list=action_list,
        log=log,
        live=live,
        blanks=blanks,
    )


def simulation(live_rounds, blank_rounds):
    loaded_shells_count = live_rounds + blank_rounds

    turn_count = 0

    for combination in combinations(range(loaded_shells_count), live_rounds):
        for action_list in product([1, 0], repeat=loaded_shells_count):
            current_load = np.zeros(loaded_shells_count)
            current_load[list(combination)] = 1

            player1 = Player("Player 1")
            player2 = Player("Player 2")

            current_load = current_load.tolist()

            log = Log()

            simulation_step(
                current_load=current_load,
                player=player1,
                opponent=player2,
                turn_count=turn_count,
                action_list=list(action_list),
                log=log,
                # log=[str(current_load), str(action_list)],
                live=live_rounds,
                blanks=blank_rounds,
            )


if __name__ == "__main__":
    #with open("log.csv", "w") as file:
    #    file.write("first_action,P1_lost_hp,P2_lost_hp,next_turn\n")
#
    #simulation(2, 2)

    df = pd.read_csv("log.csv")
    df = df.groupby(["first_action"]).agg({"P1_lost_hp": "mean", "P2_lost_hp": "mean"}).reset_index()
    df.to_csv("average_lost_hp.csv", index=False)
