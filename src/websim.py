# coding=utf-8
import logging
import time
import datetime

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import numpy as np
import pandas as pd
import config
from string import Formatter


class Recipe(object):

    def __init__(self, id, template, description=""):
        assert isinstance(id, str), "Id must be string HUUUMAN"
        assert isinstance(template, str), "Template must be string HUUUMAN"
        assert isinstance(description, str), "Description must be string HUUUMAN"
        self.id = id
        self.template = template
        self.variables = [i[1] for i in Formatter().parse(template)]
        self.description = description


class Alpha(object):
    REGIONS_UNIVERSE = {'USA': ['TOP3000', 'TOP2000', 'TOP1000', 'TOP500', 'TOP200'],
                        'EUR': ['TOP1200', 'TOP800', 'TOP600', 'TOP400', 'TOP100'],
                        'ASI': ['TOP1500', 'TOP1000', 'TOP500', 'TOP150']}

    REGIONS_DELAY = {'USA': ['1', '0'],
                     'EUR': ['1', '0'],
                     'ASI': ['1']}

    NEUTRALIZATIONS = ['None', 'Market', 'Industry', 'Subindustry']

    LOOKBACKS = ['25', '50', '128', '256', '384', '512']

    alpha_stats = ['year', 'booksize', 'long_count', 'short_count', 'pnl', 'sharpe', 'fitness',
                   'returns', 'draw_down', 'turn_over', 'margin']

    stats = {}

    def __init__(self, region, universe, delay, decay, max_stock_weight, neutralization, lookback_days, text):
        assert isinstance(region, str), 'Region of the alpha must be simple string HUUUMAN'
        assert isinstance(universe, str), 'Universe of the alpha must be simple string HUUUMAN'
        assert isinstance(text, list), 'Text of the alpha must be list HUUUMAN'
        assert isinstance(delay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(decay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(max_stock_weight, float) or isinstance(max_stock_weight,
                                                                 int), 'Max stock weight of the alpha must be simple float or integer like 0 HUUUMAN'
        assert isinstance(neutralization, str), 'Neutralization of the alpha must be simple string HUUUMAN'
        assert isinstance(lookback_days, int), 'Lookback days must be simple integer HUUUMAN'

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
        # первая буква заглавная, делаем так, чтобы без проблем можно было выставлять значение в селекторе,
        # не форматируя ничего в коде заливания альфы
        neutralization = neutralization.capitalize()
        if neutralization in Alpha.NEUTRALIZATIONS:
            self.neutralization = neutralization
        else:
            raise ValueError("Got unexpected neutralization value: {}. Possible values are {}".format(neutralization,
                                                                                                      str(
                                                                                                          Alpha.NEUTRALIZATIONS)))

        if str(lookback_days) in Alpha.LOOKBACKS:
            self.lookback_days = lookback_days
        else:
            raise ValueError("Got unexpected lookback days value: {}. Possible values are {}".format(lookback_days, str(
                Alpha.LOOKBACKS)))

    @property
    def text_str(self):
        res = ""
        for elem in self.text:
            res += elem + "\n"
        return res

    def __str__(self):
        return \
            """
            Alpha object:
            {region}
            {universe}
            {text}
            {delay}
            {decay}
            {max_stock_weight}
            {neutralization}
            {lookback_days}
            """.format(
                region=self.region,
                universe=self.universe,
                text=self.text,
                delay=self.delay,
                decay=self.decay,
                max_stock_weight=self.max_stock_weight,
                neutralization=self.neutralization,
                lookback_days=self.lookback_days
            )


class WebSim(object):
    def __init__(self, implicitly_wait=120):

        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            os.makedirs('../logs/')
        except OSError:
            pass
        hdlr = logging.FileHandler('logs/{}.log'.format(self.__class__.__name__))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1366x768')
        self.driver = webdriver.Chrome(chrome_options=options,
                                       executable_path=config.CHROMEDRIVER_PATH)
        self.driver.implicitly_wait(
            implicitly_wait)  # будет ждать implicitly_wait секунд появления элемента на странице
        self.date = datetime.datetime.now().__str__().split()[0]
        self.login_time = -1

    def __del__(self):
        self.driver.quit()

    def login(self, relog=False):
        try:
            if relog:
                self.driver.get('https://websim.worldquantchallenge.com/logout')

            self.driver.get('https://websim.worldquantchallenge.com/en/cms/wqc/websim/')
            log_pass = self.driver.find_elements_by_class_name('form-control')
            log_pass[0].clear(), log_pass[0].send_keys(config.EMAIL)
            log_pass[1].clear(), log_pass[1].send_keys(config.PASSWORD)
            log_pass[1].send_keys(Keys.RETURN)

            self.login_time = time.time()
            time.sleep(10)
            return True
        except Exception as e:
            self.logger.error("Couldn't log in")
            self.logger.error(str(e))
            return False
            # find dashboard element

    def _get_stats(self):
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

    def simulate_alpha(self, alpha):
        assert isinstance(alpha, Alpha), 'Alpha must be Alpha class instance'
        try:
            self.driver.get('https://websim.worldquantchallenge.com/simulate')
            input_form = self.driver.find_element_by_class_name('CodeMirror-line')
            settings_button = self.driver.find_element_by_class_name('test-settingslink')
            region_value = self.driver.find_element_by_xpath(
                "//select[@name='region']/option[text()='{}']".format(alpha.region))
            universe_value = self.driver.find_element_by_xpath(
                "//select[@name='univid']/option[text()='{}']".format(alpha.universe))
            delay_value = self.driver.find_element_by_xpath(
                "//select[@name='delay']/option[text()='{}']".format(alpha.delay))
            neutralization_value = self.driver.find_element_by_xpath(
                "//select[@name='opneut']/option[text()='{}']".format(alpha.neutralization))
            backdays_hidden_value = self.driver.find_element_by_name('backdays')
            decay_input = self.driver.find_element_by_name('decay')
            max_stock_weight_input = self.driver.find_element_by_name('optrunc')
            sim_action_simulate = self.driver.find_elements_by_class_name('sim-action-simulate')[2]

            action_settings = ActionChains(self.driver)
            action_settings.click(input_form)
            action_settings.send_keys(alpha.text_str)
            action_settings.click(settings_button)
            action_settings.click(region_value)
            action_settings.click(universe_value)
            action_settings.click(delay_value)
            action_settings.click(decay_input)
            action_settings.send_keys(str(alpha.decay))
            action_settings.click(max_stock_weight_input)
            action_settings.send_keys(str(alpha.max_stock_weight))
            action_settings.click(neutralization_value)
            action_settings.click(backdays_hidden_value)
            action_settings.send_keys(str(alpha.lookback_days))  # not a selector actually
            action_settings.click(settings_button)
            action_settings.click(sim_action_simulate)
            action_settings.perform()

            # по идее если запихнуть это в один action, то система зависнет до тех пор, пока не появятся все элементы, но
            # это неточно, не проверял, на всякий случай делаю в раздельных action-ах
            test_btn = self.driver.find_element_by_id('test-statsBtn')
            action_test = ActionChains(self.driver)
            action_test.click(test_btn)
            action_test.perform()

            corr_button = self.driver.find_element_by_id('alphaCorrChartButton')
            action_get_corr = ActionChains(self.driver)
            action_get_corr.click(corr_button)
            action_get_corr.perform()

            corrs = dict()
            corr_block = self.driver.find_element_by_class_name('highcharts-series')
            corr_rects = corr_block.find_element_by_tag_name('rect')
            for rect_id, rect in enumerate(corr_rects):
                elem_height = rect.get_attribute('height')
                elem_width = rect.get_attribute('width')
                if (int(elem_height) == 0) and (int(elem_width) == 0):
                    continue
                else:
                    corrs[rect_id] = elem_height

            left_corr_index = min(corrs.keys())
            right_corr_index = max(corrs.keys())

            left_corr_value = -1.0 + left_corr_index * 0.1
            right_corr_value = -1.0 + right_corr_index * 0.1 + 0.1

            alpha.stats['year_by_year'] = self._get_stats()
            alpha.stats['left_corr'] = left_corr_value
            alpha.stats['right_corr'] = right_corr_value

            # self.driver.find_elements_by_class_name('col-xs-4')[2].click() # так можно кликать тоже, обертка над кнопкой
            self.driver.find_element_by_id('resultTabPanel').find_element_by_class_name(
                'menu').find_element_by_class_name('item')[3].click()
            # жмём check submission
            self.driver.find_element_by_id('checkAlphaContainer').click()
            submittable = self.driver.find_element_by_class_name('sim-alert-container').find_element_by_class_name(
                'alert-1').find_element_by_class_name('content').text()
            print(submittable)
            submittable_flag = False
            if 'success' in submittable.lower():
                submittable_flag = True

            alpha.stats['submittable'] = submittable_flag

            """
            https://s.mail.ru/FAbH/GwQ3NS9VZ
            """
        except NoSuchElementException as err:
            if self._error(err):
                pass
            else:
                exit("Couldn't login again, it can be serious issue, stopping...")
                # TODO: далее идёт принятие решение о заливании альфы
                # здесь возможны варианты, может сделать этот класс базовым? А реализацию simulate_alpha перенести на плечи
                # прогера?
                # self.driver.find_element_by_id('checkAlphaContainer').click()
                # self.driver.find_element_by_id('submitAlphaContainer').click()

    def _error(self, error):
        """
        :param error: Объект ошибки
        :return: Возвращает True, если элемент удалось дождаться и произошел успешный перелогин,
        если перелогиниться не удалось, то возвращает False
        """
        if 'CodeMirror-line' in error.msg:
            self.driver.get('https://websim.worldquantchallenge.com/simulate')
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
