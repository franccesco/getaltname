import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='gan',
    version='2.2.1',
    author='Franccesco Orozco',
    author_email='franccesco@codingdose.info',
    description='Extract subdomains from HTTPS sites',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://franccesco.github.io/getaltname/',
    packages=setuptools.find_packages(),
    install_requires=[
        'colorama',
        'pyperclip',
        'termcolor',
        'tldextract',
        'tqdm',
        'pyopenssl',
        'pyasn1',
        'ndg-httpsclient',
    ],
    entry_points={
        'console_scripts': [
            'gan = gan.__main__:main',
            'gan_api = gan.api:app'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
        ],
    )
