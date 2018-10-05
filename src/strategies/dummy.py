# coding=utf-8
import argparse

from stuff.helpers import read_components, read_recipes, BasicGrinder
from websim import WebSim

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

    websim = WebSim()
    if websim.login(relog=True):
        idx = 0
        for new_alpha in BasicGrinder(recipe, alphas_arr, begin_index=begin_index):
            print("Going to simulate alpha:")
            print(new_alpha)
            websim.simulate_alpha(new_alpha)
            new_alpha.print_stats()
            print("Current index {}".format(idx))
            idx += 1
    else:
        print("Something went wrong, try later. Maybe service is down for maintenance")
