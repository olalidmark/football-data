from setuptools import setup

setup(
    name='football-data',
    version='0.1',
    packages=['fbdata'],
    url='https://github.com/olalidmark/football-data',
    license='MIT',
    author='fantomen',
    author_email='olalidmark@gmail.com',
    description='Wrapper over the data sets provided at http://www.football-data.co.uk/data.php to easily get historical football data like shots on goal, scored goals etc. from all major european football/soccer teams.',
    keywords=['football', 'soccer', 'metrics', 'sports', 'statistics'],  # arbitrary keywords
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

    ],
    install_requires=['numpy'],
)
