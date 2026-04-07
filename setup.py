from setuptools import find_packages, setup

setup(
    name='disagro_i',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask','pytz','numpy','pandas','openpyxl','schedule','Flask-Cors','requests','sqlalchemy','psycopg2-binary','jinja2','xlsxwriter','Pillow>=10.0.0'
    ],
)