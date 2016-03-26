from setuptools import setup

setup(
    name = 'WatsonHomeAutomation',
    version = '0.0.1',
    description = "Watson Home Automation",
    platforms = ['Unix'],
    packages = [],
    scripts=[],
    install_requires=[
        'pafy',
        'youtube_dl',
        'python-mpd2',
        'crossbar[all]',
        'requests',
        'google-api-python-client',
        'SPARQLWrapper'
        ],
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'autobahn.twisted.wamplet': [
            'backend = music.music:AppSession'
        ],
    }
)
