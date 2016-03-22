from setuptools import setup

requires = [
    'requests',
    ]

test_requires = [
    'pytest',
    'tox',
    'pytest-watch',
    'pytest-cov',
]

setup(name='basic_scraper',
      version='0.0',
      description='An application that scrapes the king county website',
      classifiers=[
        "Programming Language :: Python",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      include_package_data=True,
      zip_safe=False,
      test_suite='basic_scraper',
      install_requires=requires,
      extras_require={
        "test": test_requires,
      }
      )
