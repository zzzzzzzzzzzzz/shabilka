# coding=utf-8
"""
Пример простой стратегии.
Вообще говоря в данном случае стратегия определяется тем какой гриндер используется.
Здесь используется класс BasicGrinder. По сути это просто перебор всевозможных вариантов.
Никаких направленных действий по типу "чуть-чуть подшабить turnover" здесь не происходит.


                                                    “
                                    It's up to you
                                „
                                                                        Gospel of Kulish, 6:19-21
"""


import argparse

from stuff.helpers import read_components, read_recipes, BasicGrinder, bcolors
from websim import WebSim
import pymysql
import config

if __name__=="__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--input', '-i', type=str, help='path to file with alphas', required=True)
    p.add_argument('--recipes', '-r', type=str, help='path to file with recipies', required=True)
    p.add_argument('--recipe_name', '-rn', type=str, help='id (name) of the recipe', required=True)
    p.add_argument('--begin_index', '-bi', type=int, default=0, help='index of alpha to start with for BasicGrinder', required=False)
    args = p.parse_args()

    alphas_filepath = args.input
    recipes_filepath = args.recipes
    recipe_name = args.recipe_name
    begin_index = args.begin_index
    alphas_arr = read_components(alphas_filepath)
    recipes_arr = read_recipes(recipes_filepath)
    recipe = None
    for elem in recipes_arr:
        if elem.id == recipe_name:
            recipe = elem
            break

    if not recipe:
        raise Exception("Couldn't find recipe with id {}".format(recipe_name))

    with pymysql.connect(config.DB_HOST, config.DB_USER, config.DB_USER_PASSWORD, config.DB_NAME) as cursor:
        if not recipe.to_db(cursor):
            raise Exception("Couldn't insert recipe to db")
    # close connection, thus committing changes
    websim = WebSim()
    if websim.login(relog=True):
        for new_alpha in BasicGrinder(recipe, alphas_arr, begin_index=begin_index):
            print(bcolors.BOLD + bcolors.HEADER + "Going to simulate alpha:" + bcolors.ENDC)
            print(new_alpha)
            websim.simulate_alpha(new_alpha) # есть debug=True, который сохраняет скрины, помогают понять что произошло

            if new_alpha.simulated:
                print(bcolors.BOLD + bcolors.OKGREEN + "Alpha successfully simulated" + bcolors.ENDC)
            else:
                print(bcolors.BOLD + bcolors.FAIL + "Alpha is NOT simulated correctly" + bcolors.ENDC)

            with pymysql.connect(config.DB_HOST, config.DB_USER, config.DB_USER_PASSWORD, config.DB_NAME) as cursor:
                new_alpha.to_db(cursor, recipe)

            if new_alpha.stats['submittable']:
                print(bcolors.BOLD + bcolors.OKGREEN + "Alpha is submittable" + bcolors.ENDC)
            else:
                print(bcolors.BOLD + bcolors.FAIL + "Alpha is not submittable" + bcolors.ENDC)

            """
            Примерно здесь можно начинать реализовывать свою логику, альфа просимулирована, статы записаны, вперёд!
            # your code here
            """
    else:
        print(bcolors.BOLD + bcolors.WARNING + "Something went wrong, try later. Maybe service is down for maintenance" + bcolors.ENDC)
