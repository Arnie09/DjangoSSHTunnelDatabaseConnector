from distutils.core import setup

setup(
    name='django-ssh-tunnel-database-connector',
    packages=['DjangoSSHTunnelDatabaseConnector'],
    version='0.5.1',
    license='MIT',
    description='This is a library that enables one to use django models to do CRUD operations on a database ' +
                'hosted remotely and accessible through ssh in a pythonic way',
    long_description="Detailed documentation can be found at: " +
                     "https://github.com/Arnie09/DjangoSSHTunnelDatabaseConnector",
    author='Arnab Chanda',
    author_email='arnabchanda@gmail.com',
    url='https://github.com/Arnie09/DjangoSSHTunnelDatabaseConnector',
    download_url='https://github.com/Arnie09/DjangoSSHTunnelDatabaseConnector/archive/refs/tags/0.1.tar.gz',
    keywords=['Django', 'sshtunnel', 'database'],
    install_requires=[
        'pymysql',
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
