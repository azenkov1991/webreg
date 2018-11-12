================================
Проект записи на прием пациентов
================================

Развертывание
-------------
1. Установка необходимых пакетов:

  ``sudo utility/install_os_dependencies.sh``

2. Установка intersystem cache и pythonbindings:

    ``mkdir /tmp/cachekit``

    ``chmod og+rx /tmp/cachekit``

    ``gunzip -c /home/cache-2015.2.1.705.0su-lnxrhx64.tar.gz | ( cd /tmp/cachekit ; tar xf - )``

    ``/tmp/cachekit/cinstall``

    Указать /usr/cachesys  - Это значение по умолчанию
    Select installation type - 3
    После установки в .bashrc добавить строки:

    ``export PATH=/usr/cachesys/bin:$PATH``

    ``export LD_LIBRARY_PATH=/lib64:/usr/cachesys/bin:$LD_LIBRARY_PATH``

    ``source ./bashrc``

    ``/usr/cachesys/dev/python``

    ``python3 setup3.py  install``

    Ввести директорию /usr/cachesys

3. Установка зависимостей python:

    ``sudo utility/install_python_dependencies.sh``

4.  Скопировать secrets_example.json в secrets.json. Заполнить конфиги.

5.  Сделать миграции
    ``python manage.py migrate``

6. Создать суперюзера:

    ``python manage.py createsuperuser``

7. Запустить worker celery:

    python manage.py celeryd_multi start w1 --pidfile="/tmp/%n.pid" --logfile="/var/log/celery/%n.log" --loglevel=INFO --time-limit=300

Конфигурация patient_writer
---------------------------

1. Создать сайт и профиль пользователя для patient_writer
    ``python manage.py patientwriterinitialconfig pw.skc-fmba.ru``

2. В админке в приложении Main сконфигурировать объекты Мед. учрешдения и Подразделения

3. В приложении patient_writer сконфигурировать  объекты "Настройки мед. учреждений", "Настройки подразделений", "Настройки типов слотов"

Конфигурация qmsintegration
---------------------------

1. Создать таблицу соответсвия объектов
    ``python manage.py createobjectmatchtable``
2. Настроить Базы данных Qms для каждого учреждения

3. Настроить Подразделения Qms, указав все подразделения Qms относящиеся к подразделению

4. Создать пользователя Qms, который будет создавать назначения
