import setuptools


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

install_requires = """
extr==0.0.5
"""

setuptools.setup(
    name='extr-ds',
    version='0.0.1',
    description='',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=install_requires.strip(),
    long_description=long_description,
    long_description_content_type='text/markdown',
)
