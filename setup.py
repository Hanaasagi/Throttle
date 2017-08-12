from setuptools import setup, find_packages


setup(
    name='throttle',
    version='0.1.1',
    description='throttle',
    url='https://github.com/Hanaasagi/Throttle',
    author='Hanaasagi',
    author_email='ambiguous404@gmail.com',
    packages=find_packages(),
    install_requires=['aioredis'],
    license='MIT',
)
