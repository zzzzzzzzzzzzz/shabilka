# coding=utf-8
import argparse
import json

import itertools
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from websim import Alpha, Recipe


def return_dict_combinations(d):
    assert isinstance(d, dict), "You should pass dictionary to init this object"
    allNames = sorted(d)
    combinations = itertools.product(*(d[name] for name in allNames))
    res = []
    for comb in combinations:
        res.append(zip(allNames, comb))
    return res


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
        print("Begin index is {}".format(begin_index))

    def __iter__(self):
        if not self.recipe.commutate:
            self._permutations = itertools.permutations(self.alphas, self.variables_number)
        else:
            self._permutations = itertools.combinations(self.alphas, self.variables_number)
        self._params = [].__iter__()
        self._res = None
        self._idx = 0
        return self

    def _get_next_params(self):
        params_combination = self._params.__next__()
        new_alpha_params_dict = dict(params_combination)
        new_alpha_params_dict['text'] = self._res
        new_alpha_params_dict['components'] = self._current_components
        return new_alpha_params_dict

    def _rearm_permutations(self):
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
            'pasteurize': [],
            'nanhandling': [],
        }
        self._current_components = []
        for idx, alpha in enumerate(alphas_permutation):
            obfuscated = alpha.obfuscate_text(self.recipe.variables[idx])
            self._current_components.append(alpha.hash)
            new_vars.append("var{}".format(idx))
            obfuscated[-1] = obfuscated[-1].replace(';', '')
            obfuscated[-1] = "var{idx}={alpha_end};".format(idx=idx, alpha_end=obfuscated[-1])
            res += obfuscated
            for key, val in params.items():
                attr = getattr(alpha, key)
                if attr not in val:
                    params[key].append(attr)

        for row in self.recipe.template:
            new_row = row.format(**dict(zip(self.recipe.variables, new_vars)))
            if new_row:
                res += [new_row]
        self._res = res
        print(params)
        self._params = return_dict_combinations(params).__iter__()

    def _next(self):
        try:
            new_alpha = Alpha(**self._get_next_params())
            return new_alpha
        except StopIteration:
            print("BasicGrinder: beginning to work with new permutation")
            try:
                self._rearm_permutations()
                return self._next()
            except StopIteration as e:
                print("Permutations ended, stopping")
                raise e
        except ValueError as e:
            print("Incompaitable parameters")
            print(str(e))
            print("Skipping this alpha")
            return self._next()
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
            try:
                res.append(class_(**record))
            except Exception as e:
                pass

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


def sendemail_via_gmail(gmail_user, gmail_password, to, subject, body):
    assert isinstance(to, list), "to must be list of emails"
    import smtplib

    msg = MIMEMultipart()  # create a message
    sent_from = gmail_user
    msg['From'] = sent_from
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msg=msg, from_addr=sent_from, to_addrs=[to])
        server.close()

        print('Email sent!')
    except Exception:
        print('Something went wrong during email notification sending')

if __name__ == "__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--input', '-i', type=str, help='path to file with alphas', required=True)
    args = p.parse_args()

    filepath = args.input
    alphas_arr = read_components(filepath)
    for elem in alphas_arr:
        print(elem)
