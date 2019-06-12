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

import pymysql

from init import config
from shabilka.basic import Alpha, Recipe, BasicGrinder
from shabilka.helpers import bcolors, sendemail_via_gmail
from shabilka.websim import WebSim

if __name__ == "__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--recipes', '-r', type=str, help='path to file with recipies', required=True)
    p.add_argument('--recipe_name', '-rn', type=str, help='id (name) of the recipe', required=True)
    p.add_argument('--shuffle', '-s', type=bool, default=False, help='shuffle alphas array or not', required=True)
    p.add_argument('--tags', '-t', nargs='+', default=[], help='meta tags to set to all simulated alphas',
                   required=False)
    p.add_argument('--begin_index', '-bi', type=int, default=0, help='index of alpha to start with for BasicGrinder',
                   required=False)
    args = p.parse_args()

    recipes_filepath = args.recipes
    recipe_name = args.recipe_name
    begin_index = args.begin_index
    shuffle_flag = args.shuffle
    tags = args.tags
    alpha_reader = Alpha.return_reader()
    recipe_reader = Recipe.return_reader()
    alphas_arr = Alpha.get_bunch_of_submitted_alphas()
    if shuffle_flag:
        shuffle(alphas_arr)
    recipes_arr = recipe_reader(recipes_filepath)
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
                    tags_to_set = tags
                    print(bcolors.BOLD + bcolors.HEADER + "Going to simulate alpha:" + bcolors.ENDC)
                    print(new_alpha)
                    mes = websim.simulate_alpha(new_alpha,
                                                debug=True)  # есть debug=True, который сохраняет скрины, помогают понять что произошло

                    if new_alpha.simulated:
                        print(bcolors.BOLD + bcolors.OKGREEN + "Alpha successfully simulated" + bcolors.ENDC)
                        print("Left correlation border is {}".format(new_alpha.stats['left_corr']))
                        print("Right correlation border is {}".format(new_alpha.stats['right_corr']))
                        print("Resulting stats")
                        print(new_alpha.stats['year_by_year'][-1])
                        print(new_alpha.stats['classified'])
                        with pymysql.connect(config.DB_HOST, config.DB_USER, config.DB_USER_PASSWORD,
                                             config.DB_NAME) as cursor:
                            new_alpha.to_db(cursor, recipe)

                        if new_alpha.stats['submittable']:
                            print(bcolors.BOLD + bcolors.OKGREEN + "Alpha is submittable" + bcolors.ENDC)
                            tags_to_set += ['submittable']
                            websim.submit_alpha(new_alpha)
                        else:
                            print(bcolors.BOLD + bcolors.FAIL + "Alpha is not submittable" + bcolors.ENDC)
                    else:
                        print(bcolors.BOLD + bcolors.FAIL + "Alpha is NOT simulated correctly" + bcolors.ENDC)

                    print("Websim said: {}".format(mes))
                    print("Link to simulation {}".format(websim.driver.current_url))
                    print("")

                    if new_alpha.stats['submitted']:
                        tags_to_set += ['submitted']
                        sendemail_via_gmail(config.GMAIL_USER, config.GMAIL_PASSWORD,
                                            ['dmitriy.denisenko@outlook.com'], 'Submitted alpha!',
                                            websim.driver.current_url)
                    else:
                        if \
                                (new_alpha.stats['classified'] != 'INFERIOR') \
                                        or (float(new_alpha.stats['year_by_year'][-1]['sharpe']) > 1.3
                                            and float(new_alpha.stats['year_by_year'][-1]['turn_over'][:-1]) <= 71.0
                                            and (new_alpha.stats['right_corr'] < 0.81 and new_alpha.stats[
                                            'left_corr'] > -0.81)):
                            tags_to_set += ['potential']
                            sendemail_via_gmail(config.GMAIL_USER, config.GMAIL_PASSWORD,
                                                ['dmitriy.denisenko@outlook.com'], 'New potential alpha',
                                                websim.driver.current_url)

                    websim.set_meta(new_alpha, tags=tags_to_set)
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
                    idx += 1
                    begin_index = idx

    else:
        print(
            bcolors.BOLD + bcolors.WARNING + "Something went wrong, try later. Maybe service is down for maintenance" + bcolors.ENDC)
