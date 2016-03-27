from setuptools import find_packages, setup
setup(
    name='Flask-Dmango',
    version='0.0.5',
    url='https://github.com/jungkoo/flask-dmango',
    license='BSD',
    author='jeong mincheol',
    author_email='deajang@gmail.com',
    description='Contents managements support for Flask + MongoDB applications',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    packages=find_packages(),
    package_data={'':['templates/admin/*.html', 'templates/dmango/*.html']},
    install_requires=[
        'Flask >= 0.',
        'pymongo >= 3.2.2',
        'Flask-PyMongo >= 0.3.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    # setup_requires=['nose'],
    # tests_require=['nose', 'coverage'],
    # test_suite='nose.collector',
)
