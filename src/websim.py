# coding=utf-8
import json
import logging
import time
import datetime

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from hashlib import md5

import config
from string import Formatter


class Recipe(object):
    """
    Базовый класс рецепта.
    Переменные в template это просто именованные значения для функции .format().
    Например, {A} + {B} - две переменные А и B
    """
    def __init__(self, id, template, description=""):
        assert isinstance(id, str), "Id must be string HUUUMAN"
        assert isinstance(template, str), "Template must be string HUUUMAN"
        assert isinstance(description, str), "Description must be string HUUUMAN"
        self.id = id
        self.template = template
        self.variables = [i[1] for i in Formatter().parse(template)]
        self.description = description

    def _check_db_existance(self, cursor):
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
        if not self._check_db_existance(cursor):
            try:
                query = \
                    """
                    INSERT INTO recipes (id, description, template) VALUES ('{id}', '{description}', '{template}')
                    """.format(id=self.id, description=self.description, template=self.template)
                cursor.execute(query)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            print("This recipe is already in db: {id}".format(id=self.id))
            return True


class Alpha(object):
    """
    Базовый класс Alpha, с объектами класса Alpha работают методы класса Websim
    """

    REGIONS_UNIVERSE = {'USA': ['TOP3000', 'TOP2000', 'TOP1000', 'TOP500', 'TOP200'],
                        'EUR': ['TOP1200', 'TOP800', 'TOP600', 'TOP400', 'TOP100'],
                        'ASI': ['TOP1500', 'TOP1000', 'TOP500', 'TOP150']}

    REGIONS_DELAY = {'USA': ['1', '0'],
                     'EUR': ['1', '0'],
                     'ASI': ['1']}

    NEUTRALIZATIONS = ['None', 'Market', 'Industry', 'Subindustry']

    PASTEURIZE = ['On', 'Off']

    NANHANDLING = ['On', 'Off']

    alpha_stats = ['year', 'booksize', 'long_count', 'short_count', 'pnl', 'sharpe', 'fitness',
                   'returns', 'draw_down', 'turn_over', 'margin']

    stats = {
        'submittable': False,
        'submitted': False,
        'year_by_year': []
    }

    ASSOCIATED_DB_TABLE = 'alphas'
    ASSOCIATED_STATS_DB_TABLE = 'alphas_stats'

    def __init__(self, region, universe, delay, decay, max_stock_weight, neutralization, pasteurize, nanhandling, text, components=[]):
        assert isinstance(region, str), 'Region of the alpha must be simple string HUUUMAN'
        assert isinstance(universe, str), 'Universe of the alpha must be simple string HUUUMAN'
        assert isinstance(text, list), 'Text of the alpha must be list HUUUMAN'
        assert isinstance(delay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(decay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(max_stock_weight, float) or isinstance(max_stock_weight, int), 'Max stock weight of the alpha must be simple float or integer like 0 HUUUMAN'
        assert isinstance(neutralization, str), 'Neutralization of the alpha must be simple string HUUUMAN'
        assert isinstance(pasteurize, str), 'Pasteurize must be simple str HUUUMAN'
        assert isinstance(nanhandling, str), 'Nanhandling must be simple str HUUUMAN'
        assert isinstance(components, list), 'Components must be list type HUUUMAN'

        if region.upper() in Alpha.REGIONS_UNIVERSE:
            self.region = region.upper()
            if universe.upper() in Alpha.REGIONS_UNIVERSE[self.region]:
                self.universe = universe.upper()
            else:
                raise ValueError("Got unexpected universe value: {}. Possible values for chosen region are {}".format(
                    universe.upper(), str(Alpha.REGIONS_UNIVERSE[self.region])))
        else:
            raise ValueError('Got unexpected region value: {}. Possible values are {}'.format(region.upper(), str(
                list(Alpha.REGIONS_UNIVERSE.keys()))))
        new_text = []
        for elem in text:
            new_text.append(elem.lower())
        self.text = new_text
        if str(delay) in Alpha.REGIONS_DELAY[self.region]:
            self.delay = delay
        else:
            raise ValueError("Got unexpected delay value: {}. Possible values are {}".format(delay, str(
                Alpha.REGIONS_DELAY[self.region])))
        self.decay = decay
        if max_stock_weight >= 0.0:
            self.max_stock_weight = max_stock_weight
        else:
            raise ValueError(
                "Got unexpected max_stock_weight value: {}. Max stock value must be greater or equal than zero".format(
                    max_stock_weight))

        neutralization = neutralization.capitalize()
        if neutralization in Alpha.NEUTRALIZATIONS:
            self.neutralization = neutralization
        else:
            raise ValueError("Got unexpected neutralization value: {}. Possible values are {}".format(neutralization,
                                                                                                      str(
                                                                                                          Alpha.NEUTRALIZATIONS)))

        pasteurize = pasteurize.capitalize()
        if pasteurize in Alpha.PASTEURIZE:
            self.pasteurize = pasteurize
        else:
            raise ValueError("Got unexpected pasteurize value: {}. Possible values are {}".format(pasteurize, str(Alpha.PASTEURIZE)))

        nanhandling = nanhandling.capitalize()
        if nanhandling in Alpha.NANHANDLING:
            self.nanhandling = nanhandling
        else:
            raise ValueError("Got unexpected nanhandling value: {}. Possible values are {}".format(nanhandling, str(Alpha.NANHANDLING)))

        self.simulated = False
        if components:
            self.components = components
        else:
            self.components = []

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
            res += elem
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

    def _check_db_existance(self, cursor):
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

    def to_json_str(self):
        d = dict(
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
        return json.dumps(d)

    def to_db(self, cursor, recipe):
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
        if self.simulated:
            if not self._check_db_existance(cursor):
                try:
                    query = \
                        """
                        INSERT INTO alphas (md5hash, author, submittable, submitted, recipe_id, components, skeleton) 
                        VALUES ('{md5hash}', '{author}', {submittable}, {submitted}, '{recipe_id}', '{components}', '{skeleton}')
                        """.format(md5hash=self.hash,
                                   author=config.DB_USER,
                                   submittable=self.stats['submittable'],
                                   submitted=self.stats['submitted'],
                                   recipe_id=recipe.id,
                                   components=json.dumps(self.components),
                                   skeleton=self.to_json_str()
                                   )
                    if self.stats['submitted']:
                        query = \
                            """
                            INSERT INTO alphas (md5hash, author, submittable, submitted, submitted_time, recipe_id, components, skeleton) 
                            VALUES ('{md5hash}', '{author}', {submittable}, {submitted}, '{submitted_time}', '{recipe_id}', '{components}', '{skeleton}')
                            """.format(md5hash=self.hash,
                                       author=config.DB_USER,
                                       submittable=self.stats['submittable'],
                                       submitted=self.stats['submitted'],
                                       submitted_time=datetime.datetime.now(),
                                       recipe_id=recipe.id,
                                       components=json.dumps(self.components),
                                       skeleton=self.to_json_str()
                                       )
                    cursor.execute(query)

                    query = \
                    """
                    SELECT id FROM alphas WHERE md5hash='{md5hash}'
                    """.format(md5hash=self.hash)
                    cursor.execute(query)
                    d = cursor.fetchone()
                    alpha_id = None
                    if d:
                        alpha_id = d[0]
                    else:
                        raise Exception("Couldn't find inserted alpha")

                    for stat in self.stats['year_by_year']:
                        query = \
                        """
                        INSERT INTO alphas_stats (alpha_id, year, fitness, returns, sharpe, long_count, short_count, margin, turn_over, draw_down, booksize, pnl, left_corr, right_corr)
                        VALUES ({alpha_id}, '{year}', {fitness}, {returns}, {sharpe}, {long_count}, {short_count}, {margin}, {turn_over}, {draw_down}, {booksize}, {pnl}, {left_corr}, {right_corr})
                        """.format(alpha_id=alpha_id,
                                   year=stat['year'],
                                   fitness=stat['fitness'],
                                   returns=stat['returns'][:-1],
                                   sharpe=stat['sharpe'],
                                   long_count=stat['long_count'],
                                   short_count=stat['short_count'],
                                   margin=stat['margin'][:-3],
                                   turn_over=stat['turn_over'][:-1],
                                   draw_down=stat['draw_down'][:-1],
                                   booksize=stat['booksize'][:-1],
                                   pnl=stat['pnl'][:-1],
                                   left_corr=self.stats['left_corr'],
                                   right_corr=self.stats['right_corr'])
                        cursor.execute(query)
                    return True
                except Exception as e:
                    print(e)
                    return False
            else:
                print("This alpha is already in db")
                if self.stats['submitted']:
                    print("Now it's submitted, updating field, submitted_time")
                    try:
                        query = \
                        """
                        UPDATE alphas
                        SET submitted_time='{submitted_time}'
                        WHERE md5hash='{md5hash}'
                        """.format(submitted_time=datetime.datetime.now(),
                                   md5hash=self.hash)
                        cursor.execute(query)
                    except Exception as e:
                        print(e)
                        return False
                return True
        else:
            print("Simulate alpha before inserting it to db!")
            return False

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


class WebSim(object):
    """
    Базовый класс вебсим, через него взаимодействуем с сайтом wq
    """
    def __init__(self, implicitly_wait=120):

        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            os.makedirs('../logs/')
        except OSError:
            pass
        hdlr = logging.FileHandler('../logs/{}.log'.format(self.__class__.__name__))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1366x768')
        self.driver = webdriver.Chrome(chrome_options=options,
                                       executable_path=config.CHROMEDRIVER_PATH)
        self.implicitly_wait = implicitly_wait
        self.driver.implicitly_wait(
            implicitly_wait)  # будет ждать implicitly_wait секунд появления элемента на странице
        self.date = datetime.datetime.now().__str__().split()[0]
        self.login_time = -1

    def __del__(self):
        """
        Не забываем убивать драйвер (процесс хрома)
        :return: None
        """
        self.driver.quit()

    def login(self, relog=False):
        """
        Данные берутся из конфига
        :param relog: если флаг relog True, то предварительно идёт запрос страницы симуляции, чтобы после логина
        перекинуло куда надо
        :return: True в случае успешного логина, False иначе
        """
        try:
            if relog:
                self.driver.get('https://www.worldquantvrc.com/simulate')

            self.driver.get('https://www.worldquantvrc.com/login')
            try:
                self.driver.implicitly_wait(10)
                self.driver.find_element_by_class_name('cookie-consent-accept').click()
            except Exception:
                print("Already signed cookie")
            self.driver.implicitly_wait(self.implicitly_wait) # setting implicitly wait back
            log_pass = self.driver.find_elements_by_class_name('form-control')
            log_pass[0].clear(), log_pass[0].send_keys(config.EMAIL)
            log_pass[1].clear(), log_pass[1].send_keys(config.PASSWORD)
            log_pass[1].send_keys(Keys.RETURN)

            self.login_time = time.time()
            time.sleep(10)
            print("Login successuful")
            return True
        except Exception as e:
            self.logger.error("Couldn't log in")
            self.logger.error(str(e))
            return False
            # find dashboard element

    def _get_stats(self):
        """
        Возвращает статистику год за годом
        :return: list of dicts
        """
        table = self.driver.find_elements_by_class_name('standard-row')
        stats = []
        for row_id, row in enumerate(table):
            data = row.find_elements_by_tag_name('td')
            stats.append(
                {
                    'year': data[1].text,
                    'booksize': data[2].text,
                    'long_count': data[3].text,
                    'short_count': data[4].text,
                    'pnl': data[5].text,
                    'sharpe': data[6].text,
                    'fitness': data[7].text,
                    'returns': data[8].text,
                    'draw_down': data[9].text,
                    'turn_over': data[10].text,
                    'margin': data[11].text
                }
            )
        return stats

    def simulate_alpha(self, alpha, debug=False):
        """
        Симулирует одну альфу, выставляет настройки, вставляет текст, жмёт на нужные кнопки
        :param alpha: объект класса Alpha
        :return: ничего не возвращает, выкинет исключение в случае ошибки
        """
        assert isinstance(alpha, Alpha), 'alpha must be Alpha class instance'
        try:
            self.driver.get('https://www.worldquantvrc.com/simulate')
            self.driver.find_element_by_id("test-flowsexprCode") # switching to fast expressions
            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')
            input_form = self.driver.find_element_by_class_name('CodeMirror-line')
            # TODO: remove CodeMirror events from the input form. It substitutes symbols
            # self.driver.execute_script('''
            #
            # ''', input_form)
            settings_button = self.driver.find_element_by_class_name('test-settingslink')
            region_select = Select(self.driver.find_element_by_name('region'))
            universe_select = Select(self.driver.find_element_by_name('univid'))
            delay_select = Select(self.driver.find_element_by_name('delay'))
            neutralization_select = Select(self.driver.find_element_by_name('opneut'))
            pasteurize_select = Select(self.driver.find_element_by_name('pasteurize'))
            nanhandling_select = Select(self.driver.find_element_by_name('nanhandling'))
            # backdays_hidden_value = self.driver.find_element_by_name('backdays')  # not visible selector, custom field
            decay_input = self.driver.find_element_by_name('decay')
            max_stock_weight_input = self.driver.find_element_by_name('optrunc')
            sim_action_simulate = self.driver.find_element_by_class_name('sim-action-simulate')

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            input_form.click()
            set_input_action = ActionChains(self.driver)
            set_input_action.send_keys(alpha.text_str)
            set_input_action.perform()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            settings_button.click()
            region_select.select_by_visible_text(alpha.region)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            universe_select.select_by_visible_text(alpha.universe)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            delay_select.select_by_visible_text(str(alpha.delay))

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            neutralization_select.select_by_visible_text(alpha.neutralization)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            pasteurize_select.select_by_visible_text(alpha.pasteurize)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

            nanhandling_select.select_by_visible_text(alpha.nanhandling)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

            decay_input.clear()
            decay_input.send_keys(str(alpha.decay))

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            max_stock_weight_input.clear()
            max_stock_weight_input.send_keys(str(alpha.max_stock_weight))
            """
            # no lookback for fast expressions
            self.driver.execute_script('''
                var elem = arguments[0];
                var value = arguments[1];
                elem.value = value;
            ''', backdays_hidden_value, "512") # old lookback_days option
            """
            settings_button.click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            sim_action_simulate.click()
            test_btn = self.driver.find_element_by_id('test-statsBtn')
            test_btn.click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            corr_button = self.driver.find_element_by_id('alphaCorrChartButton')
            action_get_corr = ActionChains(self.driver)
            action_get_corr.click(corr_button)
            action_get_corr.perform()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            corrs = dict()
            corr_block = self.driver.find_element_by_class_name('highcharts-series')
            corr_rects = corr_block.find_elements_by_tag_name('rect')
            for rect_id, rect in enumerate(corr_rects):
                elem_height = rect.get_attribute('height')
                elem_width = rect.get_attribute('width')
                if (int(elem_height) == 0) and (int(elem_width) == 0):
                    continue
                else:
                    corrs[rect_id] = elem_height

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            left_corr_index = min(corrs.keys())
            right_corr_index = max(corrs.keys())

            left_corr_value = -1.0 + left_corr_index * 0.1
            right_corr_value = -1.0 + right_corr_index * 0.1 + 0.1

            alpha.stats['year_by_year'] = self._get_stats()
            alpha.stats['left_corr'] = left_corr_value
            alpha.stats['right_corr'] = right_corr_value

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            """
            Структура столбцов корреляции
            https://s.mail.ru/FAbH/GwQ3NS9VZ
            """

            # self.driver.find_elements_by_class_name('col-xs-4')[2].click() # так можно кликать тоже, обертка над кнопкой
            self.driver.find_element_by_id('resultTabPanel').find_element_by_class_name(
                'menu').find_elements_by_class_name('item')[3].click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            # жмём check submission
            self.driver.find_element_by_id('checkAlphaContainer').click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            submittable = self.driver.find_element_by_class_name('sim-alert-container').find_element_by_class_name('alert-1').find_element_by_class_name('content').text
            submittable_flag = False
            if 'success' in submittable.lower():
                submittable_flag = True

            alpha.stats['submittable'] = submittable_flag
            alpha.stats['submitted'] = False
            alpha.simulated = True

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

        except NoSuchElementException as err:
            print("Something went wrong...")
            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')
            if self._error(err):
                pass
            else:
                print("Couldn't login again, it can be serious issue, stopping...")
                exit(str(err))

    def submit_alpha(self, alpha):
        """
        Сабмитит альфу. Предполагается, что браузер уже находится на вкладке с кнопкой submit
        :param alpha: объект класса Alpha. Только что просимулированная альфа
        :return: True если альфа засабмитилась, False иначе.
        Также выставляет флаг submitted в словаре stats
        """
        assert isinstance(alpha, Alpha), 'alpha must be Alpha class instance'
        if alpha.stats['submittable']:
            self.driver.find_element_by_id('submitAlphaContainer').click()
            submittable = self.driver.find_element_by_class_name('sim-alert-container').find_element_by_class_name('alert-1').find_element_by_class_name('content').text
            if 'success' in submittable.lower():
                alpha.stats['submitted'] = True
            else:
                alpha.stats['submitted'] = False
            return alpha.stats['submitted']

    def _error(self, error):
        """
        :param error: Объект ошибки
        :return: Возвращает True, если элемент удалось дождаться и произошел успешный перелогин,
        если перелогиниться не удалось, то возвращает False
        """
        if 'CodeMirror-line' in error.msg:
            self.driver.get('https://www.worldquantvrc.com/simulate')
            try:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'CodeMirror-line'))
                WebDriverWait(self.driver, 120).until(element_present)
                # WebDriverWait(self.driver, 120).until(element_present).click()
                return True

            except TimeoutException:
                return self.login(relog=True)

        if 'test-statsBtn' in error.msg:
            try:
                element_present = EC.presence_of_element_located((By.ID, 'test-statsBtn'))
                WebDriverWait(self.driver, 180).until(element_present)
                # WebDriverWait(self.driver, 180).until(element_present).click()
                return True

            except TimeoutException:
                return self.login(relog=True)
