================================
Проект записи на прием пациентов
================================

Deployment
----------
1. Установка необходимых пакетов:

   $ sudo utility/install_os_dependencies.sh

2. Установка intersystem cache и pythonbindings:

    $ mkdir /tmp/cachekit

    $ chmod og+rx /tmp/cachekit

    $ gunzip -c /home/cache-2015.2.1.705.0su-lnxrhx64.tar.gz | ( cd /tmp/cachekit ; tar xf - )

    $ /tmp/cachekit/cinstall

    Указать /usr/cachesys  - Это значение по умолчанию
    Select installation type - 3
    После установки в .bashrc добавить строки:

    $ export PATH=/usr/cachesys/bin:$PATH

    $ export LD_LIBRARY_PATH=/lib64:/usr/cachesys/bin:$LD_LIBRARY_PATH

    $source ./bashrc

    $ cd /usr/cachesys/dev/python

    $ python3 setup3.py  install

    Ввести директорию /usr/cachesys

3. Установка зависимостей python:

    $ sudo utility/install_python_dependencies.sh

4.  Скопировать secrets_example.json в secrets.json. Заполнить конфиги.

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* Создать суперюзера:


    $ python manage.py createsuperuser --settings=config.settings.local.py

* Запустить worker celery:

    python manage.py celeryd_multi start w1 --pidfile="/tmp/%n.pid" --logfile="/var/log/celery/%n.log" --loglevel=INFO --time-limit=300
