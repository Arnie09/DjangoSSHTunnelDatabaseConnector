from distutils.core import setup

setup(
    name='DjangoSSHTunnelDatabaseConnector',
    packages=['DjangoSSHTunnelDatabaseConnector'],
    version='0.1',
    license='MIT',
    description='This is a library that enables one to use django models to do CRUD operations on a database ' +
                'hosted remotely and accessible through ssh in a pythonic way',
    author='Arnab Chanda',
    author_email='arnabchanda@gmail.com',
    url='https://github.com/user/reponame',
    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',
    keywords=['Django', 'sshtunnel', 'database'],
    install_requires=[
        'pymysql',
        'logging',
        'sshtunnel'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
