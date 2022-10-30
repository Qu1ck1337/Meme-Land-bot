import discord

from classes.DataBase import update_user_exp, get_user


def count_to_next_level(current_level):
    exp = 25 + current_level * 15
    return exp


def add_user_exp(user_id: int, exp: int):
    user = get_user(user_id)
    added_exp = user["exp"] + exp
    level = user["level"]
    if added_exp >= count_to_next_level(user["level"]):
        added_exp -= count_to_next_level(user["level"])
        level += 1
    update_user_exp(user, added_exp, level)