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


class Alpha(object):
    REGIONS_UNIVERSE = {'USA': ['TOP3000', 'TOP2000', 'TOP1000', 'TOP500', 'TOP200'],
                        'EUR': ['TOP1200', 'TOP800', 'TOP600', 'TOP400', 'TOP100'],
                        'ASI': ['TOP1500', 'TOP1000', 'TOP500', 'TOP150']}

    REGIONS_DELAY = {'USA': ['1', '0'],
                     'EUR': ['1', '0'],
                     'ASI': ['1']}

    NEUTRALIZATIONS = ['None', 'Market', 'Industry', 'Subindustry']

    LOOKBACKS = ['25', '50', '128', '256', '384', '512']

    def __init__(self, region, universe, delay, decay, max_stock_weight, neutralization, lookback_days, text):
        assert isinstance(region, str), 'Region of the alpha must be simple string HUUUMAN'
        assert isinstance(universe, str), 'Universe of the alpha must be simple string HUUUMAN'
        assert isinstance(text, str), 'Text of the alpha must be simple string HUUUMAN'
        assert isinstance(delay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(decay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(max_stock_weight, float), 'Max stock weight of the alpha must be simple float HUUUMAN'
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
        self.text = text.lower()
        if str(delay) in Alpha.REGIONS_DELAY[self.region]:
            self.delay = delay
        else:
            raise ValueError("Got unexpected delay value: {}. Possible values are {}".format(delay, str(
                Alpha.REGIONS_DELAY[self.region])))
        self.decay = decay
        if max_stock_weight > 0.0:
            self.max_stock_weight = max_stock_weight
        else:
            raise ValueError(
                "Got unexpected max_stock_weight value: {}. Max stock value must be greater than zero".format(
                    max_stock_weight))

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


alpha_stats = ['alpha', 'year', 'long_count', 'short_count', 'pnl', 'sharpe', 'fitness',
               'returns', 'draw_down', 'turn_over', 'margin']


class WebSim(object):
    def __init__(self, implicitly_wait=60):

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
        self.driver.implicitly_wait(60)  # будет ждать implicitly_wait секунд появления элемента на странице
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

    def stats(self, i, alpha):
        table = self.driver.find_elements_by_class_name('standard-row')
        for row_id, row in enumerate(table):
            data = row.find_elements_by_tag_name('td')
            self.res_df.alpha.iloc[i * 7 + row_id] = alpha
            self.res_df.year.iloc[i * 7 + row_id] = data[1].text
            self.res_df.long_count.iloc[i * 7 + row_id] = data[3].text
            self.res_df.short_count.iloc[i * 7 + row_id] = data[4].text
            self.res_df.pnl.iloc[i * 7 + row_id] = data[5].text
            self.res_df.sharpe.iloc[i * 7 + row_id] = data[6].text
            self.res_df.fitness.iloc[i * 7 + row_id] = data[7].text
            self.res_df.returns.iloc[i * 7 + row_id] = data[8].text
            self.res_df.draw_down.iloc[i * 7 + row_id] = data[9].text
            self.res_df.turn_over.iloc[i * 7 + row_id] = data[10].text
            self.res_df.margin.iloc[i * 7 + row_id] = data[11].text

    # TODO: сделать метод для симуляции одной альфы
    def simulate_alpha(self, alpha):
        assert isinstance(alpha, Alpha), 'Alpha must be Alpha class instance'
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
        action_settings.send_keys(alpha.text)
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

        """
        https://s.mail.ru/FAbH/GwQ3NS9VZ
        """

        # TODO: далее идёт принятие решение о заливании альфы
        # self.driver.find_elements_by_class_name('col-xs-4')[2].click() # так можно кликать тоже, обертка над кнопкой
        self.driver.find_element_by_id('resultTabPanel').find_element_by_class_name('menu').find_element_by_class_name('item')[3].click()

        # здесь возможны варианты, может сделать этот класс базовым? А реализацию simulate_alpha перенести на плечи
        # прогера?
        self.driver.find_element_by_id('checkAlphaContainer').click()
        self.driver.find_element_by_id('submitAlphaContainer').click()

        # self.stats(i, alpha)

    def simulate(self, alphas_df, res_df=None, i_start=None):
        """
        Берёт датафрейм с альфами, и прогоняет в вебсиме
        :param alphas_df: датафрейм с альфами
        :param res_df: результирующий датафрейм
        :param i_start: индекс начала в датафрейме с альфами
        :return:
        """
        if res_df is None:
            res_df = pd.DataFrame(index=range(alphas_df.shape[0] * 7), columns=alpha_stats)

        if i_start is None:
            i_start = res_df.dropna(how='all').shape[0] / 7
            # i_start = (res_df.dropna(how='all').index[-1] + 1) / 7

        self.res_df = res_df
        self.alphas_df = alphas_df

        while (1):
            try:
                for i in range(alphas_df.shape[0])[i_start:]:
                    alpha = alphas_df.iloc[i][0]

                    self.driver.get('https://websim.worldquantchallenge.com/simulate')
                    self.driver.find_element_by_class_name('CodeMirror-line').click()

                    action = ActionChains(self.driver)
                    action.send_keys(alpha)
                    action.perform()

                    self.driver.find_elements_by_class_name('col-xs-4')[2].click()
                    self.driver.find_element_by_id('test-statsBtn').click()

                    self.stats(i, alpha)
                    if i % 30 == 0:
                        # промежуточные результаты
                        # save_df.iloc[save_start * 7:(i + 1) * 7] = res_df.iloc[save_start * 7:(i + 1) * 7]
                        res_df.to_csv(self.date + '_simulate.csv', index=False)
                        save_start = i + 1

                    if int(time.time()) - self.login_time > 10800:
                        # перелогин
                        if self.login(relog=True):
                            self.login_time = int(time.time())
                        else:
                            exit(-1)

            except NoSuchElementException as err:
                if not self.error(err, i):
                    i_start = i + 1
                else:
                    i_start = i

            if i == alphas_df.shape[0] - 1:
                # пишем финальный результат
                res_df.to_csv(self.date + '_simulate.csv', index=False)
                break

    def error(self, error, i):
        """

        :param error:
        :param i:
        :return:
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
