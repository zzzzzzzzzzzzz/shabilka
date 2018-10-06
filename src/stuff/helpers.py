# coding=utf-8
import argparse
import json

import itertools

from websim import Alpha, Recipe


class RoundRobin(object):
    """
    Бесконечный итератор по массиву
    """

    def __init__(self, arr):
        assert isinstance(arr, list) or isinstance(arr,
                                                   tuple), "To perform round robin you should pass array-like object"
        self.arr = arr
        self._to_yield_idx = 0
        self._length = len(self.arr)

    def __iter__(self):
        self._to_yield_idx = 0
        self._length = len(self.arr)
        return self

    def __next__(self):
        i = self._to_yield_idx
        self._to_yield_idx += 1
        return self.arr[i % self._length]


class DictRoundRobin(object):
    """
    Возвращает все комбинации структуры типа {'a':[1,2], 'b':[3,4,5],...}
    Когда все комбинации кончились выбрасывает StopIteration
    """

    def __init__(self, d):
        assert isinstance(d, dict), "You should pass dictionary to init this object"
        self.d = d
        self._r = 0
        self._robins = {}

    def __iter__(self):
        if self.d:
            self._r = 1
            for k, v in self.d.items():
                self._r *= len(v)
                self._robins[k] = RoundRobin(v)
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < self._r:
            to_return = []
            for k, v in self._robins.items():
                self._idx += 1
                to_return.append((k, v.__next__()))
            return to_return
        else:
            raise StopIteration


class BasicGrinder(object):
    """
    Базовый гриндер.
    Берёт на вход рецепт, массив альф и перебирает всевозможные перестановки (размера количества переменных в
    шаблоне) и параметры "в колесе".
    """
    def __init__(self, recipe, alphas, begin_index=0):
        assert isinstance(recipe, Recipe), "recipe must be Recipe class instance"
        assert isinstance(alphas, list), "alphas must be list"
        for elem in alphas:
            assert isinstance(elem, Alpha), "Each element of the alphas list must be Alpha class instance"
        self.recipe = recipe
        self.alphas = alphas
        self._robin = None
        self.variables_number = len(self.recipe.variables)
        self.begin_index = begin_index
        print("Got {} alphas".format(len(self.alphas)))
        print("Gor recipe {}".format(self.recipe.id))
        print("Number of variables {}".format(self.variables_number))

    def __iter__(self):
        self._permutations = itertools.permutations(self.alphas, self.variables_number)
        self._params = DictRoundRobin({}).__iter__()
        self._res = None
        self._idx = 0
        return self

    def _get_next_params(self):
        params_combination = self._params.__next__()  # вылетает на первой итерации
        new_alpha_params_dict = dict(params_combination)
        new_alpha_params_dict['text'] = self._res
        new_alpha_params_dict['lookback_days'] = 512
        return new_alpha_params_dict

    def _next(self):
        try:
            return Alpha(**self._get_next_params())
        except StopIteration:
            try:
                alphas_permutation = self._permutations.__next__()
                res = []
                new_vars = []
                params = {
                    'region': [],
                    'universe': [],
                    'decay': [],
                    'delay': [],
                    'max_stock_weight': [],
                    'neutralization': [],
                }
                for idx, alpha in enumerate(alphas_permutation):
                    new_vars.append("var{}".format(idx))
                    old_ending = alpha.text[-1]
                    alpha.text[-1] = alpha.text[-1].replace(';', '')
                    alpha.text[-1] = "var{idx}={alpha_end};".format(idx=idx, alpha_end=alpha.text[-1])
                    res += alpha.text
                    alpha.text[-1] = old_ending
                    for key, val in params.items():
                        attr = getattr(alpha, key)
                        if attr not in val:
                            params[key].append(attr)

                res += [self.recipe.template.format(**dict(zip(self.recipe.variables, new_vars)))]
                self._res = res
                self._params = DictRoundRobin(params).__iter__()
                return Alpha(**self._get_next_params())
            except StopIteration as e:
                print("Permutations ended, stopping")
                raise e
            except Exception as e:
                print("Caught an exception during iteration. Stopping and writing the last index")
                with open('../logs/' + self.__class__.__name__ + '_stopped_on.log', 'w') as f:
                    f.write(str(self._idx))
                raise e

    def __next__(self):
        while self._idx < self.begin_index:
            self._next()
            self._idx += 1
        self._idx += 1
        return self._next()


def read_init(classname):
    def read(filepath):
        module = __import__('websim')
        class_ = getattr(module, classname)

        with open(filepath, 'r') as f:
            records_json = json.load(f)

        res = []
        for record in records_json:
            res.append(class_(**record))

        return res

    return read


read_components = read_init('Alpha') # читалка альф из файла типа components.json
read_recipes = read_init('Recipe') # читалка рецептов из файла типа recipes.json


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--input', '-i', type=str, help='path to file with alphas', required=True)
    args = p.parse_args()

    filepath = args.input
    alphas_arr = read_components(filepath)
    for elem in alphas_arr:
        print(elem)
