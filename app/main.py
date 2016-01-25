""" A very simple Flask application.
"""

import flask
from flask.ext.sqlalchemy import SQLAlchemy

class Configuration(object):
    LIVE_SERVER_PORT = 5000
    TEST_SERVER_PORT = 5000
    SQLALCHEMY_TRACK_MODIFICATIONS = False

application = flask.Flask(__name__)
application.config.from_object(Configuration)
database = SQLAlchemy(application)


@application.route("/<int:fraction>/<int:total>")
def frontpage(fraction, total):
    template = """<!DOCTYPE>
    <html><title>Percent</title>
    <body><h1>{}</h1></body>
    </html>"""
    if fraction > total:
        return template.format("Invalid: Fraction greater than Total")
    if total == 0:
        percent = '0'
    else:
        percent = str(int(100 * (float(fraction) / float(total))))
    result = "{} of {} is {}%".format(fraction, total, percent)
    return template.format(result)


# Now for some testing.
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pytest
# Currently just used for the temporary hack to quit the phantomjs process
# see below in quit_driver.
import signal


def test_my_server():  #pragma: no cover
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.implicitly_wait(5)

    def get_url(local_url):
        port = application.config['TEST_SERVER_PORT']
        url = 'http://localhost:{0}'.format(port)
        return "/".join([url, local_url])

    def get_percent_url(fraction, total):
        local_url = "{}/{}".format(fraction, total)
        return get_url(local_url)

    def check_fraction(fraction, total, expected):
        driver.get(get_percent_url(fraction, total))
        h1_css = 'body h1'
        h1 = driver.find_element_by_css_selector(h1_css)
        assert h1.text == expected

    try:
        check_fraction(50, 100, '50 of 100 is 50%')
        check_fraction(20, 30, '20 of 30 is 66%')
        check_fraction(50, 10, 'Invalid: Fraction greater than Total')
        check_fraction(0, 0, '0 of 0 is 0%')

    finally:
        driver.get(get_url('shutdown'))
        driver.close()
        # A bit of hack this but currently there is some bug I believe in
        # the phantomjs code rather than selenium, but in any case it means that
        # the phantomjs process is not being killed so we do so explicitly here
        # for the time being. Obviously we can remove this when that bug is
        # fixed. See: https://github.com/SeleniumHQ/selenium/issues/767
        driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()
