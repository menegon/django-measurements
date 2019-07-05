from setuptools import setup, find_packages

setup(
    name='django-measurements',
    version='0.10',
    # packages=['measurements'],
    packages=find_packages(),
    url='',
    license='GPL3',
    author='Stefano Menegon',
    author_email='stefano.menegon@cnr.it',
    description='', install_requires=['django', 'numpy', 'pandas',
                                      'urllib3', 'requests', 'pycryptodome',
                                      'django-postgres-extra', 'django_pandas']
)
