# coding=utf-8
import datetime
import json
import re
from hashlib import md5
from string import Formatter
from typing import Optional, List

import os

import itertools

import math
import pymysql

from init.config import DB_USER, DB_HOST, DB_USER_PASSWORD, DB_NAME, LOGDIR
import constants

from shabilka import websim
from shabilka.helpers import read_init, return_dict_combinations

logger = websim.logger

flatten = lambda l: [item for sublist in l for item in sublist]


class Recipe(object):
    """
    Базовый класс рецепта.
    Переменные в template это просто именованные значения для функции .format().
    Например, {A} + {B} - две переменные А и B
    """

    def __init__(self, id, template, description="", commutate=True):
        assert isinstance(id, str), "Id must be string HUUUMAN"
        assert isinstance(template, list), "Template must be list HUUUMAN"
        assert isinstance(description, str), "Description must be string HUUUMAN"
        assert isinstance(commutate, bool), "Commutate must be boolean HUUUMAN"
        self.id = id
        self.template = template
        self.commutate = commutate
        variables = set()

        for row in template:
            for i in Formatter().parse(row):
                if i[1]:
                    variables.add(i[1])

        self.variables = list(variables)
        self.description = description

    @property
    def row_template(self):
        res = ""
        for row in self.template:
            res += row + '\n'
        return res

    def check_db_existance(self, cursor):
        """
        По имени (id) проверяет наличие рецепта в таблице recipes
        :param cursor: объект курсора базы данных mysql
        :return: True если рецепт есть, False иначе
        """
        query = \
            """
            SELECT 1 FROM recipes WHERE id='{id}' 
            """.format(id=self.id)
        cursor.execute(query)
        if cursor.fetchone():
            return True
        else:
            return False

    def to_db(self, cursor):
        """
        Отправляет рецепт (шаблон) в таблицу recipes
        :param cursor: объект курсора базы данных mysql
        :return: True если добавление успешно, False иначе, если рецепт уже был в таблице, то вернёт True
        """
        if not self.check_db_existance(cursor):
            try:
                query = \
                    """
                    INSERT INTO recipes (id, commutate, description, template) VALUES ('{id}', {commutate}, '{description}', '{template}')
                    """.format(id=self.id, commutate=self.commutate, description=self.description,
                               template=self.row_template)
                cursor.execute(query)
                return True
            except Exception as e:
                raise e
        else:
            logger.warning("This recipe is already in db: {id}".format(id=self.id))
            return True

    @classmethod
    def return_reader(cls):
        return read_init(cls)


class Alpha(object):
    """
    Базовый класс Alpha, с объектами класса Alpha работают методы класса Websim
    """

    REGIONS_UNIVERSE = {'USA': ['TOP3000', 'TOP2000', 'TOP1000', 'TOP500', 'TOP200'],
                        'EUR': ['TOP1200', 'TOP800', 'TOP600', 'TOP400', 'TOP100'],
                        'ASI': ['TOP1500', 'TOP1000', 'TOP500', 'TOP150']}

    REGIONS_DELAY = {'USA': [1, 0],
                     'EUR': [1, 0],
                     'ASI': [1]}

    NEUTRALIZATIONS = ['None', 'Market', 'Sector', 'Industry', 'Subindustry']

    PASTEURIZE = ['On', 'Off']

    NANHANDLING = ['On', 'Off']

    alpha_stats = ['year', 'booksize', 'long_count', 'short_count', 'pnl', 'sharpe', 'fitness',
                   'returns', 'draw_down', 'turn_over', 'margin']

    stats = {
        'submittable': False,
        'submitted': False,
        'classified': 'INFERIOR',
        'year_by_year': []
    }

    letters_multipliers = {
        'K': 1e3,
        'M': 1e6
    }

    ASSOCIATED_DB_TABLE = 'alphas'
    ASSOCIATED_STATS_DB_TABLE = 'alphas_stats'

    DEFAULT_REGION = 'USA'
    DEFAULT_REGIONS_UNIVERSE = {
        'USA': 'TOP3000',
        'EUR': 'TOP1200',
        'ASI': 'TOP1500'
    }
    DEFAULT_REGIONS_DELAY = {
        'USA': 1,
        'EUR': 1,
        'ASI': 1
    }
    DEFAULT_DECAY = 0
    DEFAULT_MAX_STOCK_WEIGHT = 0.03
    DEFAULT_NEUTRALIZATION = "Market"
    DEFAULT_PASTEURIZE = 'On'
    DEFAULT_NANHANDLING = 'On'

    def __init__(self, components=(), **kwargs):
        assert isinstance(components, list), 'Components must be list type HUUUMAN'

        # region init
        if 'region' in kwargs:
            region = kwargs['region']
            if region.upper() in self.REGIONS_UNIVERSE:
                self.region = region.upper()
            else:
                raise ValueError('Got unexpected region value: {}. Possible values are {}'.format(region.upper(), str(
                    list(self.REGIONS_UNIVERSE.keys()))))
        else:
            self.region = self.DEFAULT_REGION

        # universe init
        if 'universe' in  kwargs:
            universe = kwargs['universe']
            if universe.upper() in self.REGIONS_UNIVERSE[self.region]:
                self.universe = universe.upper()
            else:
                raise ValueError("Got unexpected universe value: {}. Possible values for chosen region are {}".format(
                    universe.upper(), str(self.REGIONS_UNIVERSE[self.region])))
        else:
            self.universe = self.DEFAULT_REGIONS_UNIVERSE[self.region]

        # delay init
        if 'delay' in kwargs:
            delay = int(kwargs['delay'])
            if delay in self.REGIONS_DELAY[self.region]:
                self.delay = delay
            else:
                raise ValueError("Got unexpected delay value: {}. Possible values are {}".format(delay, str(
                    self.REGIONS_DELAY[self.region])))
        else:
            self.delay = self.DEFAULT_REGIONS_DELAY[self.region]

        # decay init
        if 'decay' in kwargs:
            self.decay = int(kwargs['decay'])
        else:
            self.decay = self.DEFAULT_DECAY

        # max stock weight init
        if 'max_stock_weight' in kwargs:
            max_stock_weight = float(kwargs['max_stock_weight'])
            if max_stock_weight >= 0.0:
                self.max_stock_weight = max_stock_weight
            else:
                raise ValueError(
                    "Got unexpected max_stock_weight value: {}. Max stock value must be float greater or equal than "
                    "zero".format(
                        max_stock_weight))
        else:
            self.max_stock_weight = self.DEFAULT_MAX_STOCK_WEIGHT

        # neutralization init
        if 'neutralization' in kwargs:
            neutralization = kwargs['neutralization'].capitalize()
            neutralization = neutralization.capitalize()
            if neutralization in self.NEUTRALIZATIONS:
                self.neutralization = neutralization
            else:
                raise ValueError("Got unexpected neutralization value: {}. Possible values are {}".format(neutralization,
                                                                                                      str(
                                                                                                          self.NEUTRALIZATIONS)))
        else:
            self.neutralization = self.DEFAULT_NEUTRALIZATION

        # pasteurize init
        if 'pasteurize' in kwargs:
            pasteurize = kwargs['pasteurize'].capitalize()
            pasteurize = pasteurize.capitalize()
            if pasteurize in self.PASTEURIZE:
                self.pasteurize = pasteurize
            else:
                raise ValueError(
                    "Got unexpected pasteurize value: {}. Possible values are {}".format(pasteurize, str(self.PASTEURIZE)))
        else:
            self.pasteurize = self.DEFAULT_PASTEURIZE

        # nanhandling init
        if 'nanhandling' in kwargs:
            nanhandling = kwargs['nanhandling'].capitalize()
            nanhandling = nanhandling.capitalize()
            if nanhandling in self.NANHANDLING:
                self.nanhandling = nanhandling
            else:
                raise ValueError("Got unexpected nanhandling value: {}. Possible values are {}".format(nanhandling, str(
                    self.NANHANDLING)))
        else:
            self.nanhandling = self.DEFAULT_NANHANDLING

        # text init
        if 'text' in kwargs:
            text = kwargs['text']
            assert isinstance(text, list), 'Text of the alpha must be list'
            new_text = []
            for elem in text:
                new_text.append(elem.lower())
            self.text = new_text
        else:
            raise AttributeError("text parameter is required!")

        self.simulated = False
        self.components = components

        if not self._check_correctness():
            raise ValueError("This alpha is not valid for such universe, region, delay options")

    def print_stats(self):
        """
        Красиво выводит статы альфы
        :return: None
        """
        for k, v in self.stats.items():
            print(k, v)

    @property
    def text_str(self):
        """
        Представление текста альфы как строчки (вместо массива)
        :return: строка - текст альфы
        """
        res = ""
        for elem in self.text:
            res += elem + '  \n'
        return res

    @property
    def hash(self):
        """
        md5 хэш альфы, nuff said
        ЛУЧШЕ ВОТ ЭТО ВОТ ВООБЩЕ БОЛЬШЕ НЕ ТРОГАТЬ
        :return: hexdigest md5
        пример:
        In [6]: md5('123'.encode('utf-8')).hexdigest()
        Out[6]: '202cb962ac59075b964b07152d234b70'
        """
        return md5(
            (str(self.region) +
             str(self.universe) +
             str(self.text) +
             str(self.delay) +
             str(self.decay) +
             str(self.max_stock_weight) +
             str(self.neutralization) +
             str(self.pasteurize) +
             str(self.nanhandling)).encode('utf-8')
        ).hexdigest()

    def check_db_existance(self, cursor):
        """
        Производит проверку наличия альфы по хэшу в таблице alphas
        :param cursor: объект курсора базы mysql
        :return: True, если альфа есть в таблице alphas, False иначе
        """
        query = \
            """
            SELECT 1 FROM alphas WHERE md5hash='{md5hash}'
            """.format(md5hash=self.hash)
        cursor.execute(query)
        if cursor.fetchone():
            return True
        else:
            return False

    def return_params(self):
        return dict(
            text=self.text,
            region=self.region,
            universe=self.universe,
            decay=self.decay,
            delay=self.delay,
            max_stock_weight=self.max_stock_weight,
            neutralization=self.neutralization,
            pasteurize=self.pasteurize,
            nanhandling=self.nanhandling
        )

    def to_json_str(self):
        return json.dumps(self.return_params())

    def to_db(self, cursor, recipe: Optional[Recipe]=None):
        """
        Отправляет все данные связанные с альфой в базу данных.

        Логика следующая. Альфа в любом случае должна быть просимулирована.
        При вызове сначала проверяется присутствие альфы в базе.
        Если альфы в базе нет, то производится вставка в таблицы alphas и alphas_stats,
        если же альфа уже есть в базе, то в случае если в self.stats['submitted'] выставлено True, произойдет вызов sql
        запроса Update, который выставит флаг submitted в базе в True, если же self.stats['submitted'] False, то ничего
        не произойдёт и вернётся True.
        Обратите внимание, что если несколько раз вызывать to_db на альфе с self.stats['submitted'] True, то будет
        перезаписываться время сабмита (submitted_time).
        :param cursor: объект курсора базы mysql
        :param recipe: объект класса Recipe
        :return: True если удалось вставить альфу в таблицу, False иначе, при этом если запись уже была, вернётся True
        """

        recipe_id = "dummy"
        if recipe:
            recipe_id = recipe.id

        if self.simulated:
            if not self.check_db_existance(cursor):
                try:
                    query = \
                        """
                        INSERT INTO {table} (md5hash, author, submittable, submitted, classified, recipe_id, components, skeleton) 
                        VALUES ('{md5hash}', '{author}', {submittable}, {submitted}, '{classified}', '{recipe_id}', '{components}', '{skeleton}')
                        """.format(table=self.ASSOCIATED_DB_TABLE,
                                   md5hash=self.hash,
                                   author=DB_USER,
                                   submittable=self.stats['submittable'],
                                   submitted=self.stats['submitted'],
                                   classified=self.stats['classified'],
                                   recipe_id=recipe_id,
                                   components=json.dumps(self.components),
                                   skeleton=pymysql.escape_string(self.to_json_str())
                                   )

                    if self.stats['submitted']:
                        query = \
                            """
                            INSERT INTO {table} (md5hash, author, submittable, submitted, classified, submitted_time, recipe_id, components, skeleton) 
                            VALUES ('{md5hash}', '{author}', {submittable}, {submitted}, '{classified}', '{submitted_time}', '{recipe_id}', '{components}', '{skeleton}')
                            """.format(table=self.ASSOCIATED_DB_TABLE,
                                       md5hash=self.hash,
                                       author=DB_USER,
                                       submittable=self.stats['submittable'],
                                       submitted=self.stats['submitted'],
                                       classified=self.stats['classified'],
                                       submitted_time=datetime.datetime.now(),
                                       recipe_id=recipe_id,
                                       components=json.dumps(self.components),
                                       skeleton=pymysql.escape_string(self.to_json_str())
                                       )
                    cursor.execute(query)

                    query = \
                        """
                    SELECT id FROM {table} WHERE md5hash='{md5hash}'
                    """.format(table=self.ASSOCIATED_DB_TABLE, md5hash=self.hash)
                    cursor.execute(query)
                    d = cursor.fetchone()
                    alpha_id = None
                    if d:
                        alpha_id = d[0]
                    else:
                        raise Exception("Couldn't find inserted alpha")
                    numbers_regexp = re.compile('[\d\.]+')
                    for stat in self.stats['year_by_year']:
                        pnl_multiplier = 1.0
                        pnl = stat.get('pnl', '0.0K')
                        if pnl[-1] in self.letters_multipliers:
                            pnl_multiplier = self.letters_multipliers[pnl[-1]]
                        query = \
                            """
                        INSERT INTO {table} (alpha_id, year, fitness, returns, sharpe, long_count, short_count, margin, turn_over, draw_down, booksize, pnl, left_corr, right_corr)
                        VALUES ({alpha_id}, '{year}', {fitness}, {returns}, {sharpe}, {long_count}, {short_count}, {margin}, {turn_over}, {draw_down}, {booksize}, {pnl}, {left_corr}, {right_corr})
                        """.format(table=self.ASSOCIATED_STATS_DB_TABLE,
                                   alpha_id=alpha_id,
                                   year=numbers_regexp.findall(stat.get('year', '0000'))[0],
                                   fitness=stat.get('fitness', 0),
                                   returns=numbers_regexp.findall(stat.get('returns', '0.00%'))[0],
                                   sharpe=stat.get('sharpe', 0.0),
                                   long_count=stat.get('long_count', 0),
                                   short_count=stat.get('short_count', 0),
                                   margin=numbers_regexp.findall(stat.get('margin', '999.9bpm'))[0],
                                   turn_over=numbers_regexp.findall(stat.get('turn_over', '0.00%'))[0],
                                   draw_down=numbers_regexp.findall(stat.get('draw_down', '0.00%'))[0],
                                   booksize=numbers_regexp.findall(stat.get('booksize', '20.0M'))[0],
                                   pnl=float(numbers_regexp.findall(pnl)[0])*pnl_multiplier,
                                   left_corr=math.ceil(float(self.stats.get('left_corr', 0.0))),
                                   right_corr=math.floor(float(self.stats.get('right_corr', 0.0))))
                        cursor.execute(query)
                    return True
                except Exception as e:
                    raise e
            else:
                logger.warning("This alpha is already in db")
                if self.stats['submitted']:
                    logger.info("Now it's submitted, updating field, submitted_time")
                    try:
                        query = \
                            """
                        UPDATE {table}
                        SET submitted_time='{submitted_time}'
                        WHERE md5hash='{md5hash}'
                        """.format(table=self.ASSOCIATED_DB_TABLE,
                                   submitted_time=datetime.datetime.now(),
                                   md5hash=self.hash)
                        cursor.execute(query)
                    except Exception as e:
                        raise e

                return True
        else:
            raise Exception("Simulate alpha before inserting it to db!")

    def __str__(self):
        return \
            """
            Alpha object:
            {text}
            {region}
            {universe}
            {delay}
            {decay}
            {max_stock_weight}
            {neutralization}
            {pasteurize}
            {nanhandling}
            """.format(
                region=self.region,
                universe=self.universe,
                text=self.text,
                delay=self.delay,
                decay=self.decay,
                max_stock_weight=self.max_stock_weight,
                neutralization=self.neutralization,
                pasteurize=self.pasteurize,
                nanhandling=self.nanhandling
            )

    def pretty_print_text(self):
        for row in self.text:
            print(row)

    def _return_variables_and_special_words(self, variables_flag=True, other_words_flag=True, grouping_words_flag=True,
                                            operator_words_flag=True, data_words_flag=True):
        variables_list = []
        special_words_list = []
        other_words_list = []
        grouping_words_list = []
        operator_words_list = []
        data_words_list = []
        for row in self.text:
            for word in re.findall(r'\b[a-zA-Z_]+[0-9_]*[a-zA-Z_]*\b',
                                   row):  # допускает такие переменные как x, alpha2b, alpha_2b
                word_lower = word.lower()
                found = False
                if other_words_flag:
                    if word_lower in constants.OTHER_WORDS.keys():
                        found = True
                        other_words_list.append(word)

                if grouping_words_flag:
                    if word_lower in constants.GROUPING_WORDS.keys():
                        found = True
                        grouping_words_list.append(word)

                if operator_words_flag:
                    if word_lower in constants.OPERATOR_WORDS:
                        found = True
                        operator_words_list.append(word)

                if data_words_flag:
                    for key, value in constants.DATA_WORDS.items():
                        if word_lower in value.keys():
                            found = True
                            data_words_list.append(word)
                            break

                if variables_flag:
                    if not found:
                        variables_list.append(word)

        special_words_list = other_words_list + grouping_words_list + operator_words_list + data_words_list

        return variables_list, special_words_list

    def _check_correctness(self):
        variables, specials = self._return_variables_and_special_words(other_words_flag=False,
                                                                       grouping_words_flag=False,
                                                                       operator_words_flag=False)
        import pymysql
        with pymysql.connect(DB_HOST, DB_USER, DB_USER_PASSWORD, DB_NAME) as cursor:
            for word in specials:
                query = \
                    """
                    SELECT 
                      1 
                    FROM 
                      data_words
                    WHERE
                      data_name='{data_name}'
                      AND 
                      region='{region}'
                      AND 
                      delay={delay}
                """.format(
                        data_name=word.lower(),
                        region=self.region.lower(),
                        delay=self.delay
                    )
                cursor.execute(query)
                if not cursor.fetchone():
                    logger.error("found incompaitable with {} {} {} special word '{}'".format(self.universe.lower(),
                                                                                       self.region.lower(), self.delay,
                                                                                       word))
                    return False

        return True

    def obfuscate_text(self, suffix):
        variables_list, specials = self._return_variables_and_special_words()
        result = self.text.copy()
        for var in variables_list:
            regex = re.compile(r'\b{}\b'.format(var))

            tmp = []
            for row in result:
                tmp.append(re.sub(regex, var + suffix, row))

            result = tmp

        return result

    @classmethod
    def commutative(cls, alphas_list, params_alpha_idx: Optional[int], params: Optional[dict], action: str ="+"):
        """
        Adds alphas from alphas_list as
        alpha_1 action alpha_2 action ... action alpha_n
        and returns the new alpha.
        :param action: commutative operator. Such as "+", "-" or "*"
        :param alphas_list: List of Alpha instances
        :param params_alpha_idx: will inherit params from alphas_list[params_alpha_idx], if not None will use this
        :param params: if not None and params_alpha_idx is None the new alpha inherit these params
        :return: new cls object
        """
        # криво, но ничего лучше для проверки alphas_list я не придумал
        def inner(alphas_list: List[cls], params_alpha_idx, params, action):
            if (params_alpha_idx is None) and (params is None):
                raise ValueError("You should pass params_alpha_idx or params dict")

            new_alpha_text = []
            for i in range(len(alphas_list)):
                current_alpha_text = alphas_list[i].text.copy()
                current_alpha_text[-1] = "toadd_{}=".format(i) + current_alpha_text[-1] + ";"
                new_alpha_text += current_alpha_text

            new_alpha_text += ["tosimulate=" + ["toadd_{}".format(j) for j in range(len(alphas_list))].join(action)]

            new_components = list(set(flatten([alphas_list[i].components for i in range(len(alphas_list))])))
            if params_alpha_idx is not None:
                # inherit params
                inherit_alpha = alphas_list[params_alpha_idx]
                new_params = {
                    "region": inherit_alpha.region,
                    "universe": inherit_alpha.universe,
                    "delay": inherit_alpha.delay,
                    "decay": inherit_alpha.decay,
                    "max_stock_weight": inherit_alpha.max_stock_weight,
                    "neutralization": inherit_alpha.neutralization,
                    "pasteurize": inherit_alpha.pasteurize,
                    "nanhandling": inherit_alpha.nanhandling,
                    "text": new_alpha_text,
                    "components": new_components
                }
                return Alpha(**new_params)
            else:
                # use params
                params['text'] = new_alpha_text
                params['components'] = new_components
                return Alpha(**params)

        return inner(alphas_list, params_alpha_idx, params, action)

    @classmethod
    def wrap_str_function(cls, alphas_list, func: str, params_alpha_idx: Optional[int], params: Optional[dict], *args, **kwargs):
        """
        Wraps alphas to websim function with params.
        Unsafe method, you should figure out which params are required for this function.
        Which of them are named and not named and if the special order is required.
        :param params: if not None and params_alpha_idx is None the new alpha inherit these params
        :param params_alpha_idx: will inherit params from alphas_list[params_alpha_idx], if not None will use this
        :param alphas_list: list of Alpha objects
        :param func: str name of the function
        :param args: list of argument for this websim function
        :param kwargs: dictionary of named arguments for this websim function
        :return: new cls object wrapped in func
        """
        def inner(alphas_list: List[cls], func, params_alpha_idx, params, *args, **kwargs):
            if (params_alpha_idx is None) and (params is None):
                raise ValueError("You should pass params_alpha_idx or params dict")

            new_alpha_text = []
            for i in range(len(alphas_list)):
                current_alpha_text = alphas_list[i].text.copy()
                current_alpha_text[-1] = "toapply_{}=".format(i) + current_alpha_text[-1] + ";"
                new_alpha_text += current_alpha_text

            pass_to_func = ["toapply_{}".format(j) for j in range(len(alphas_list))] + args + ["{}={}".format(key, value)
                                                                                               for key, value in
                                                                                               kwargs.items()]
            new_alpha_text += ["tosimulate={}(".format(func) + pass_to_func.join(',')]
            new_components = list(set(flatten([alphas_list[i].components for i in range(len(alphas_list))])))

            if params_alpha_idx is not None:
                # inherit params
                inherit_alpha = alphas_list[params_alpha_idx]
                new_params = {
                    "region": inherit_alpha.region,
                    "universe": inherit_alpha.universe,
                    "delay": inherit_alpha.delay,
                    "decay": inherit_alpha.decay,
                    "max_stock_weight": inherit_alpha.max_stock_weight,
                    "neutralization": inherit_alpha.neutralization,
                    "pasteurize": inherit_alpha.pasteurize,
                    "nanhandling": inherit_alpha.nanhandling,
                    "text": new_alpha_text,
                    "components": new_components
                }
                return Alpha(**new_params)
            else:
                # use params
                params['text'] = new_alpha_text
                params['components'] = new_components
                return Alpha(**params)

        return inner(alphas_list, func, params_alpha_idx, params, args, kwargs)

    @classmethod
    def return_reader(cls):
        return read_init(cls)

    @classmethod
    def load_to_db_from_file(cls, filepath, wbsm, debug=False):
        resimulate_list = []
        websim_messages_list = []
        folder = os.path.join(LOGDIR, 'alpha_load_to_db_from_file/')
        try:
            os.makedirs(folder)
        except Exception:
            pass
        try:
            if wbsm.login(relog=True):
                reader = cls.return_reader()
                alphas_arr = reader(filepath)
                for alpha in alphas_arr:
                    connection = pymysql.connect(DB_HOST, DB_USER, DB_USER_PASSWORD, DB_NAME)
                    try:
                        with connection.cursor() as cursor:
                            if alpha.check_db_existance(cursor):
                                logger.error("Alpha is already in db, skipping. Hash {}".format(alpha.hash))
                                continue
                        connection.commit()
                    finally:
                        connection.close()
                    try:
                        mes = None
                        mes = wbsm.simulate_alpha(alpha, debug=debug)
                        logger.debug("Alpha simulated flag is {}".format(alpha.simulated))
                        logger.debug("Alpha hash {}".format(alpha.hash))
                        if alpha.simulated:
                            alpha.stats['submitted'] = 1
                            connection = pymysql.connect(DB_HOST, DB_USER, DB_USER_PASSWORD, DB_NAME)
                            try:
                                with connection.cursor() as cursor:
                                    alpha.to_db(cursor)

                                connection.commit()
                            finally:
                                connection.close()
                        else:
                            logger.info("Websim said: {}".format(mes))
                            resimulate_list.append(alpha.return_params())
                            if mes:
                                websim_messages_list.append(mes)
                    except Exception as e:
                        logger.error("Caught an exception")
                        logger.error(str(e))
                        logger.info("Will add this alpha to resimulate list")
                        logger.info("Websim said: {}".format(mes))
                        resimulate_list.append(alpha.return_params())
                        if mes:
                            websim_messages_list.append(mes)
        finally:
            logger.debug(resimulate_list)
            with open(os.path.join(folder, "resimulate.json"), "w") as f:
                json.dump(obj=resimulate_list, fp=f)

            with open(os.path.join(folder, "websim_messages.json"), "w") as f:
                json.dump(obj=websim_messages_list, fp=f)

    @classmethod
    def get_bunch_of_submitted_alphas(cls, bunch_size=10, additional_filtering=""):
        """
        Берёт случайное подмножество альф из базы
        :param bunch_size: сколько альф взять из базы
        :param additional_filtering: дополнительная фильтрация, ожидается корректный sql код типа "AND ..."
        :return: список проинизиализированных объектов альф из базы
        """
        result = []
        connection = pymysql.connect(DB_HOST, DB_USER, DB_USER_PASSWORD, DB_NAME)
        try:
            with connection.cursor() as cursor:
                query = \
                    """
                    SELECT 
                      components,
                      skeleton 
                    FROM
                      {table}
                    WHERE
                      submitted=TRUE 
                      {additional_filtering}
                    ORDER BY RAND()
                    LIMIT {bunch_size}
                    """.format(
                        table=cls.ASSOCIATED_DB_TABLE,
                        bunch_size=bunch_size,
                        additional_filtering=""
                    )

                cursor.execute(query)
                for elem in cursor.fetchall():
                    result.append(cls(
                        components=json.loads(elem[0]),
                        **json.loads(elem[1])
                    ))
            connection.commit()
            return result
        finally:
            connection.close()


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
        logger.info("Got {} alphas".format(len(self.alphas)))
        logger.info("Gor recipe {}".format(self.recipe.id))
        logger.info("Number of variables {}".format(self.variables_number))
        logger.info("Begin index is {}".format(begin_index))

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
            obfuscated = alpha.obfuscate_text('_'+str(idx))
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
        logger.info(params)
        self._params = return_dict_combinations(params).__iter__()

    def _next(self):
        try:
            new_alpha = Alpha(**self._get_next_params())
            return new_alpha
        except StopIteration:
            logger.info("BasicGrinder: beginning to work with new permutation")
            try:
                self._rearm_permutations()
                return self._next()
            except StopIteration as e:
                logger.info("Permutations ended, stopping")
                raise e
        except ValueError as e:
            logger.error("Incompaitable parameters")
            logger.error(str(e))
            logger.info("Skipping this alpha")
            return self._next()
        except Exception as e:
            logger.warning("Caught an exception during iteration. Stopping and writing the last index")
            with open(os.path.join(LOGDIR, self.__class__.__name__ + '_stopped_on.log'), 'w') as f:
                f.write(str(self._idx))
            raise e

    def __next__(self):
        while self._idx < self.begin_index:
            self._next()
            self._idx += 1
        self._idx += 1
        return self._next()
