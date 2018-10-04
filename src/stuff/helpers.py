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
        assert isinstance(arr, list) or isinstance(arr, tuple), "To perform round robin you should pass array-like object"
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
            for k, v in self.d.iteritems():
                self._r *= len(v)
                self._robins[k] = RoundRobin(v)
        self.idx = 0
        return self

    def __next__(self):
        if self.idx < self._r:
            to_return = []
            for k, v in self._robins.iteritems():
                self.idx += 1
                to_return.append((k, v.__next__()))
            return to_return
        else:
            raise StopIteration


class BasicGrinder(object):
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

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        try:
            for alphas_combination in itertools.combinations_with_replacement(self.alphas, self.variables_number):
                for alphas_permutation in itertools.permutations(alphas_combination):
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
                        alpha.text[-1] = "var{idx}={alpha_end}".format(idx=idx, alpha_end=alpha.text[-1])
                        res += alpha.text
                        for key, val in params.items():
                            attr = getattr(alpha, key)
                            if attr not in val:
                                params[key].append(attr)

                    res += [self.recipe.template.format(**dict(zip(self.recipe.variables, new_vars)))]
                    for params_combination in DictRoundRobin(params):
                        new_alpha_params_dict = dict(params_combination)
                        new_alpha_params_dict['text'] = res
                        new_alpha_params_dict['lookback_days'] = 512
                        self.idx += 1
                        if self.idx-1 < self.begin_index:
                            return None
                        else:
                            return Alpha(**new_alpha_params_dict)
        except StopIteration as e:
            raise e
        except Exception as e:
            print("Caught an exception during iteration. Stopping and writing the last index")
            with open('../logs/' + self.__class__.__str__() + '_stopped_on.log', 'w') as f:
                f.write(self.idx)
            raise e


def read_components(filepath):
    with open(filepath, 'r') as f:
        alphas_json = json.load(f)

    res = []
    for alpha in alphas_json:
        res.append(Alpha(**alpha))

    return res


if __name__ == "__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--input', '-i', type=str, help='path to file with alphas', required=True)
    args = p.parse_args()

    filepath = args.input
    alphas_arr = read_components(filepath)
    for elem in alphas_arr:
        print(elem)
