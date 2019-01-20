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
from random import shuffle

from stuff.helpers import read_components, read_recipes, BasicGrinder, bcolors, sendemail_via_gmail
from websim import WebSim
import pymysql
import config

if __name__=="__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--input', '-i', type=str, help='path to file with alphas', required=True)
    p.add_argument('--recipes', '-r', type=str, help='path to file with recipies', required=True)
    p.add_argument('--recipe_name', '-rn', type=str, help='id (name) of the recipe', required=True)
    p.add_argument('--shuffle', '-s', type=bool, default=False, help='shuffle alphas array or not', required=True)
    p.add_argument('--begin_index', '-bi', type=int, default=0, help='index of alpha to start with for BasicGrinder', required=False)
    args = p.parse_args()

    alphas_filepath = args.input
    recipes_filepath = args.recipes
    recipe_name = args.recipe_name
    begin_index = args.begin_index
    shuffle_flag = args.shuffle
    alphas_arr = read_components(alphas_filepath)
    if shuffle_flag:
        shuffle(alphas_arr)
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
        idx = begin_index
        while 1:
            try:
                for new_alpha in BasicGrinder(recipe, alphas_arr, begin_index=begin_index):
                    print(bcolors.BOLD + bcolors.HEADER + "Going to simulate alpha:" + bcolors.ENDC)
                    print(new_alpha)
                    mes = websim.simulate_alpha(new_alpha, debug=True) # есть debug=True, который сохраняет скрины, помогают понять что произошло

                    if new_alpha.simulated:
                        print(bcolors.BOLD + bcolors.OKGREEN + "Alpha successfully simulated" + bcolors.ENDC)
                        print("Left correlation border is {}".format(new_alpha.stats['left_corr']))
                        print("Right correlation border is {}".format(new_alpha.stats['right_corr']))
                        print("Resulting stats")
                        print(new_alpha.stats['year_by_year'][-1])
                        print(new_alpha.stats['classified'])
                    else:
                        print(bcolors.BOLD + bcolors.FAIL + "Alpha is NOT simulated correctly" + bcolors.ENDC)

                    with pymysql.connect(config.DB_HOST, config.DB_USER, config.DB_USER_PASSWORD, config.DB_NAME) as cursor:
                        new_alpha.to_db(cursor, recipe)

                    if new_alpha.stats['submittable']:
                        print(bcolors.BOLD + bcolors.OKGREEN + "Alpha is submittable" + bcolors.ENDC)
                    else:
                        print(bcolors.BOLD + bcolors.FAIL + "Alpha is not submittable" + bcolors.ENDC)

                    print("Websim said: {}".format(mes))

                    if new_alpha.stats['classified'] != 'INFERIOR':
                        sendemail_via_gmail(config.GMAIL_USER, config.GMAIL_PASSWORD, ['dmitriy.denisenko@outlook.com'], 'New potential alpha', websim.driver.current_url)

                    """
                    Примерно здесь можно начинать реализовывать свою логику, альфа просимулирована, статы записаны, вперёд!
                    # your code here
                    """

                    idx += 1
            except Exception as e:
                print(bcolors.BOLD + bcolors.WARNING + "Caught an exception" + bcolors.ENDC)
                print(str(e))
                if isinstance(e, KeyboardInterrupt):
                    print("Exiting by keyboard interrupt")
                    exit(0)
                else:
                    begin_index = idx+1

    else:
        print(bcolors.BOLD + bcolors.WARNING + "Something went wrong, try later. Maybe service is down for maintenance" + bcolors.ENDC)
