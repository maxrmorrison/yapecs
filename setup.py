from setuptools import find_packages, setup


with open('README.md', encoding='utf8') as file:
    long_description = file.read()


setup(
    name='yapecs',
    description='Yet Another Python Experiment Configuration System (YAPECS)',
    version='0.1.0',
    author='Max Morrison',
    author_email='maxrmorrison@gmail.com',
    url='https://github.com/maxrmorrison/yapecs',
    install_requires=['filelock'],
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['configuration', 'config', 'experiment', 'manager'])
