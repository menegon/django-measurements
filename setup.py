from setuptools import setup

setup(
    name='django-measurements',
    version='0.1',
    packages=['measurements'],
    url='',
    license='GPL3',
    author='Stefano Menegon',
    author_email='stefano.menegon@cnr.it',
    description='', install_requires=['django', 'numpy', 'pandas', 'urllib3', 'requests', 'pycryptodome']
)
