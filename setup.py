from setuptools import setup, find_packages

with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(
    name='ogham-cloud',
    version='0.0.1',
    description='ogham backend',
    author='DSP-Tan',
    author_email='danielsptanner@gmail.com',
    #url='github.com/DSP-Tan/ogham-cloud',
    packages=["pdf_scraper", "web_scraper"],
    install_requires=requirements

)