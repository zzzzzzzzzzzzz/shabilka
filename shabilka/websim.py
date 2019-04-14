# coding=utf-8
import datetime
import logging
import time

import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from shabilka import basic
from init.config import CHROMEDRIVER_PATH, EMAIL, PASSWORD, LOGDIR, GLOBAL_LOGGER

logger = GLOBAL_LOGGER


class Actions(ActionChains):
    def wait(self, time_s: float):
        self._actions.append(lambda: time.sleep(time_s))
        return self


class WebSim(object):
    """
    Базовый класс вебсим, через него взаимодействуем с сайтом wq
    """
    BASIC_URL = "https://worldquantvrc.com/"
    SIMULATE_PAGE = "https://worldquantvrc.com/simulate"
    LOGIN_PAGE = "https://worldquantvrc.com/login"

    def __init__(self, implicitly_wait=120):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1366x768')
        self.driver = webdriver.Chrome(chrome_options=options,
                                       executable_path=CHROMEDRIVER_PATH)
        self.implicitly_wait = implicitly_wait
        self.driver.implicitly_wait(
            implicitly_wait)  # будет ждать implicitly_wait секунд появления элемента на странице
        self.date = datetime.datetime.now().__str__().split()[0]
        self.login_time = -1
        
        self.simulate_logdir = os.path.join(LOGDIR, 'simulate/')
        try:
            os.makedirs(self.simulate_logdir)
        except Exception:
            pass

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
                self.driver.get(self.SIMULATE_PAGE)

            self.driver.get(self.LOGIN_PAGE)
            try:
                self.driver.implicitly_wait(10)
                self.driver.find_element_by_class_name('cookie-consent-accept').click()
            except Exception:
                logger.info("Already signed cookie")
            self.driver.implicitly_wait(self.implicitly_wait) # setting implicitly wait back
            log_pass = self.driver.find_elements_by_class_name('form-control')
            log_pass[0].clear(), log_pass[0].send_keys(EMAIL)
            log_pass[1].clear(), log_pass[1].send_keys(PASSWORD)
            log_pass[1].send_keys(Keys.RETURN)

            self.login_time = time.time()
            time.sleep(10)
            logger.info("Login successuful")
            return True
        except Exception as e:
            logger.error("Couldn't log in")
            logger.error(str(e))
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

    def simulate_alpha(self, alpha, save_chart=False, debug=False):
        """
        Симулирует одну альфу, выставляет настройки, вставляет текст, жмёт на нужные кнопки
        :param debug: дебаг режим. Будет сохранять скриншоты на каждом шаге
        :param save_chart: сохранять ли скриншот с графиком
        :param alpha: объект класса Alpha
        :return: ничего не возвращает, выкинет исключение в случае ошибки
        """
        assert isinstance(alpha, basic.Alpha), 'alpha must be Alpha class instance'

        saveshot = lambda seed: self.driver.save_screenshot(os.path.join(self.simulate_logdir, str(seed) + '.png'))

        alert_message = None

        self.driver.get(self.SIMULATE_PAGE)
        if debug:
            saveshot(datetime.datetime.now())

        # переключаемся на fast expressions
        self.driver.find_element_by_id("test-flowsexprCode").click()

        body = self.driver.find_element_by_tag_name('body')
        input_form = self.driver.find_element_by_class_name('CodeMirror-code')

        # определяем дополнительные нужные элементы на странице
        settings_button = self.driver.find_element_by_class_name('test-settingslink')
        region_select = Select(self.driver.find_element_by_name('region'))
        universe_select = Select(self.driver.find_element_by_name('univid'))
        delay_select = Select(self.driver.find_element_by_name('delay'))
        neutralization_select = Select(self.driver.find_element_by_name('opneut'))
        pasteurize_select = Select(self.driver.find_element_by_name('pasteurize'))
        nanhandling_select = Select(self.driver.find_element_by_name('nanhandling'))
        decay_input = self.driver.find_element_by_name('decay')
        max_stock_weight_input = self.driver.find_element_by_name('optrunc')
        sim_action_simulate = self.driver.find_element_by_class_name('sim-action-simulate')
        alert_container = self.driver.find_element_by_class_name('sim-alert-container')

        # и часто используемые действия
        go_to_top = Actions(self.driver)
        go_to_top.click(body)
        go_to_top.send_keys_to_element(body, Keys.CONTROL + Keys.HOME)

        go_to_end = Actions(self.driver)
        go_to_end.click(body)
        go_to_end.send_keys_to_element(body, Keys.CONTROL + Keys.END)

        escape = Actions(self.driver)
        escape.send_keys(Keys.ESCAPE)

        try:
            # убираем автодополнение
            self.driver.execute_script("$(\"head\").append(\"<style>.CodeMirror-hints { display:None }</style>\")")

            if debug:
                saveshot(datetime.datetime.now())

            # фокусируемся на поле ввода
            input_form.click()

            input_action = Actions(self.driver)

            # построчно вводим текст альфы
            # здесь остались элементы, отключающие автодополнение
            # в принципе если учесть, что его нет, то можно пихать альфу целым куском
            l = len(alpha.text)
            for idx in range(l):
                input_action.send_keys(alpha.text[idx])
                if idx != l-1:
                    input_action.key_down(Keys.LEFT_SHIFT).send_keys(Keys.ENTER).key_up(Keys.LEFT_SHIFT)

            input_action.perform()

            # текст альфы может быть большим, надо промотать наверх
            go_to_top.perform()

            if debug:
                saveshot(datetime.datetime.now())

            # тыкаем на кнопочку настроек
            settings_button.click()

            # анимация занимает какое-то время. Элемент уже есть на странице, но невидим какое-то время
            # без этого sleep-а часто будет выдавать ошибки
            time.sleep(1)

            # по очереди выставляем все нужные нам опции
            region_select.select_by_visible_text(alpha.region)

            if debug:
                saveshot(datetime.datetime.now())

            universe_select.select_by_visible_text(alpha.universe)

            if debug:
                saveshot(datetime.datetime.now())

            delay_select.select_by_visible_text(str(alpha.delay))

            if debug:
                saveshot(datetime.datetime.now())

            neutralization_select.select_by_visible_text(alpha.neutralization)

            if debug:
                saveshot(datetime.datetime.now())

            pasteurize_select.select_by_visible_text(alpha.pasteurize)

            if debug:
                saveshot(datetime.datetime.now())

            nanhandling_select.select_by_visible_text(alpha.nanhandling)

            if debug:
                saveshot(datetime.datetime.now())

            decay_input.clear()
            decay_input.send_keys(str(alpha.decay))

            if debug:
                saveshot(datetime.datetime.now())

            max_stock_weight_input.clear()
            max_stock_weight_input.send_keys(str(alpha.max_stock_weight))

            # закрываем окно настроек, здесь уже можно не ждать пока оно закроется
            settings_button.click()

            if debug:
                saveshot(datetime.datetime.now())

            # двигаемся к кнопке симуляции, текст альфы может быть большим, и она может исчезнуть за границу экрана
            go_to_end.perform()

            # запускаем симуляцию, и выставляем время ожидания побольше
            sim_action_simulate.click()
            self.driver.implicitly_wait(self.implicitly_wait*3)

            # двигаемся наверх
            go_to_top.perform()

            # объявляем элементы, связанные со статами
            resultTabPanel = self.driver.find_element_by_id('resultTabPanel')

            tab_elements = resultTabPanel.find_element_by_class_name('menu').find_elements_by_class_name('item')
            while len(tab_elements) < 4:
                # ждём пока все плашки прогрузятся, чертова анимация
                time.sleep(1)
                tab_elements = resultTabPanel.find_element_by_class_name('menu').find_elements_by_class_name('item')

            chart_btn = tab_elements[0]
            test_stats_btn = resultTabPanel.find_element_by_id('test-statsBtn')
            metadata_btn = tab_elements[2]
            submission_page = tab_elements[3]

            # переходим на вкладку статистики
            test_stats_btn.click()
            self.driver.implicitly_wait(self.implicitly_wait)

            # и опять, на всякий случай
            go_to_top.perform()

            if debug:
                saveshot(datetime.datetime.now())

            # ожидаем анимацию
            time.sleep(1)

            classified = self.driver.find_element_by_id('percentileStats').find_element_by_class_name('panel-title').get_attribute('innerText').upper()
            if classified:
                alpha.stats['classified']=classified

            # парсим корреляцию
            corr_button = self.driver.find_element_by_id('alphaCorrChartButton')
            action_get_corr = ActionChains(self.driver)
            action_get_corr.click(corr_button)
            action_get_corr.perform()

            if debug:
                saveshot(datetime.datetime.now())

            go_to_end.perform()

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
                saveshot(datetime.datetime.now())

            go_to_top.perform()

            left_corr_index = min(corrs.keys())
            right_corr_index = max(corrs.keys())

            left_corr_value = -1.0 + left_corr_index * 0.1
            right_corr_value = -1.0 + right_corr_index * 0.1 + 0.1

            # парсим статы
            alpha.stats['year_by_year'] = self._get_stats()
            alpha.stats['left_corr'] = left_corr_value
            alpha.stats['right_corr'] = right_corr_value

            if save_chart:
                # сохраняем графичек
                chart_btn.click()
                # ждём прогрузки графика
                time.sleep(3)
                saveshot(alpha.hash)

            if debug:
                saveshot(datetime.datetime.now())

            """
            Структура столбцов корреляции
            https://s.mail.ru/FAbH/GwQ3NS9VZ
            """

            submission_page.click()

            if debug:
                saveshot(datetime.datetime.now())

            check_submission_btn = self.driver.find_element_by_id('checkAlphaContainer')
            # жмём check submission
            check_submission_btn.click()

            if debug:
                saveshot(datetime.datetime.now())

            go_to_top.perform()

            submittable = alert_container.get_attribute('innerText')
            submittable_flag = False
            if 'success' in submittable.lower():
                submittable_flag = True
            else:
                alert_message = submittable # raise message why it's not submittable

            alpha.stats['submittable'] = submittable_flag
            alpha.stats['submitted'] = False
            alpha.simulated = True

            go_to_top.perform()

            if debug:
                saveshot(datetime.datetime.now())

        except NoSuchElementException as err:
            logger.error("Something went wrong...")
            alert_message = alert_container.get_attribute('innerText')
            if not alert_message:
                if debug:
                    saveshot(datetime.datetime.now())
                if not self._error(err):
                    logger.error("Couldn't login again, it can be serious issue, stopping...")
                    exit(-1)

        if debug:
            saveshot(datetime.datetime.now())

        return alert_message

    def submit_alpha(self, alpha):
        """
        Сабмитит альфу
        :param alpha: объект класса Alpha. Только что просимулированная альфа
        :return: True если альфа засабмитилась, False иначе.
        Также выставляет флаг submitted в словаре stats
        """
        assert isinstance(alpha, basic.Alpha), 'alpha must be Alpha class instance'
        alert_message = "Alpha is not submittable. Research more"
        if 'result' not in self.driver.current_url:
            alert_message = self.simulate_alpha(alpha)
        alert_container = self.driver.find_element_by_class_name('sim-alert-container')
        if alpha.stats['submittable']:
            self.driver.find_element_by_id('submitAlphaContainer').click()
            submittable = alert_container.get_attribute('innerText')
            if 'success' in submittable.lower():
                alpha.stats['submitted'] = True
            else:
                alpha.stats['submitted'] = False
            return alpha.stats['submitted']
        else:
            return alert_message

    def _error(self, error):
        """
        :param error: Объект ошибки
        :return: Возвращает True, если элемент удалось дождаться и произошел успешный перелогин,
        если перелогиниться не удалось, то возвращает False
        """
        if 'CodeMirror-line' in error.msg:
            self.driver.get(self.SIMULATE_PAGE)
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
