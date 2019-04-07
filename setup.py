from distutils.core import setup

from setuptools import find_packages

from shabilka import __version__

with open('requirements.txt', encoding='utf-8') as file:
    requirements = file.read().splitlines()

setup(
    name='shabilka',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    version=__version__,
    url='',
    license='',
    author='dmitriy',
    author_email='dmitriy.denisenko@outlook.com',
    description='Здесь мы делаем бота для вебсима, который будет помогать нам шабить альфы.  Всё, что раньше мы делали руками в перспективе должен будет делать этот бот.'
)
