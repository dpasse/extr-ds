import setuptools


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='extr-ds',
    version='0.0.18',
    keywords='',
    description='Library to quickly build basic datasets for Named Entity Recognition (NER) and Relation Extraction (RE) Machine Learning tasks.',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'extr==0.0.21'
    ],
    url='https://github.com/dpasse/extr-ds',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
