# coding=utf-8
import argparse
import datetime
import json
import re

from selenium.webdriver.common.keys import Keys

from stuff.helpers import bcolors
from websim import WebSim, Alpha
from time import sleep

if __name__ == '__main__':
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--output', '-o', type=str, help='path for the file with alphas', required=True)
    p.add_argument('--debug', '-d', type=bool, help='debug mode on/off', default=False)
    args = p.parse_args()

    alphas_f = args.output
    debug = args.debug

    websim = WebSim()

    if websim.login(relog=True):
        sleep(10)

        # basically could be done just by going to /myalphas url :)
        # ***
        if debug:
            websim.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

        navigation = websim.driver.find_elements_by_class_name('navbar-nav')[1]
        alphas_button = navigation.find_elements_by_class_name('dropdown')[0] # deal with element not visible error
        my_alphas_link = alphas_button.find_elements_by_class_name('dropdown-menu')[0].find_elements_by_tag_name('li')[1]

        alphas_button.click()
        my_alphas_link.click()

        # ***
        # end of this part

        if debug:
            websim.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

        # now we must be on alphas page

        # not clickable
        # prod_button = websim.driver.find_element_by_name('Prod')
        # hence a bit harder
        prod_button = websim.driver.find_element_by_class_name('color-btn-group').find_elements_by_tag_name('label')[1]
        prod_button.click()

        sleep(10)

        if debug:
            websim.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

        hashes = []

        while True:
            tbl_wrapper = websim.driver.find_element_by_class_name('griddle-body')
            table_body = tbl_wrapper.find_element_by_tag_name('tbody')
            alphas_rows = table_body.find_elements_by_tag_name('tr')

            for row in alphas_rows:
                link_hash = row.find_elements_by_tag_name('td')[0].find_elements_by_tag_name('span')[0].get_attribute('data-value')
                print(link_hash)
                hashes.append(link_hash)

            next_button = websim.driver.find_element_by_class_name('griddle-next')
            if next_button.size['width']:
                next_button.click()
                print("going to the next page")
                sleep(1)
                if debug:
                    websim.driver.save_screenshot(str(datetime.datetime.now()) + '.png')
            else:
                break

        print("Got {} prod alphas".format(len(hashes)))

        skipped = []
        collected = []
        idx = 1
        for h in hashes:
            print("processing {}/{} alpha".format(idx, len(hashes)))
            websim.driver.get('https://www.worldquantvrc.com/alpha/{}'.format(h))
            sleep(1)
            websim.driver.find_elements_by_class_name('tablect-menu-item')[1].click()  # alpha code page
            if debug:
                websim.driver.save_screenshot(str(datetime.datetime.now()) + '.png')
            alpha_text = []
            for elem in websim.driver.find_elements_by_class_name('CodeMirror-line'):
                line = elem.get_attribute('innerText')
                if not re.match('\\u.+', line): # drop if find some strange unicode symbols
                    line = re.sub('\/\/.+$', line, "") # removing comments
                    if line: # if it's not empty string
                        alpha_text.append(re.sub(line))
            print(alpha_text)

            # парсинг параметров
            websim.driver.find_elements_by_class_name('tablect-menu-item')[2].click()  # alpha params page
            params_table = websim.driver.find_elements_by_tag_name('table')[0]
            params_table_body = params_table.find_element_by_tag_name('tbody')
            row = params_table_body.find_elements_by_tag_name('tr')[0]
            cells = row.find_elements_by_tag_name('td')
            region = cells[2].get_attribute('innerText')
            universe = cells[3].get_attribute('innerText')
            decay = int(cells[7].get_attribute('innerText'))
            delay = int(cells[8].get_attribute('innerText'))
            max_stock_weight = float(cells[9].get_attribute('innerText'))
            neutralization = cells[10].get_attribute('innerText')
            pasteurize = "on"
            nanhandling = "off"

            if cells[12].get_attribute('innerText') != 'N/A':
                pasteurize = cells[12].get_attribute('innerText')
            if cells[13].get_attribute('innerText') != 'N/A':
                nanhandling = cells[13].get_attribute('innerText')

            try:
                a = Alpha(
                    region=region,
                    universe=universe,
                    decay=decay,
                    delay=delay,
                    max_stock_weight=max_stock_weight,
                    neutralization=neutralization,
                    pasteurize=pasteurize,
                    nanhandling=nanhandling,
                    text=alpha_text
                )

                collected.append({
                    'text': a.text,
                    'region': a.region,
                    'universe': a.universe,
                    'decay': a.decay,
                    'delay': a.delay,
                    'max_stock_weight': a.max_stock_weight,
                    'neutralization': a.neutralization,
                    'pasteurize': a.pasteurize,
                    'nanhandling': a.nanhandling
                })
            except Exception as e:
                print(str(e))
                print("Couldn't initialize Alpha object, skipping...")
                skipped.append(h)

            idx += 1

        print("This is what was skipped for some reason:\n{}".format(skipped))

        with open(alphas_f, 'w') as f:
            json.dump(collected, f)

    else:
        print(bcolors.BOLD + bcolors.WARNING + "Something went wrong, try later. Maybe service is down for maintenance" + bcolors.ENDC)
