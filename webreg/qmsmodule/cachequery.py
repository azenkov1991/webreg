# -*- coding: utf-8 -*-
from functools import reduce
from os.path import join
from datetime import date
import logging
import intersys.pythonbind3
from suds.client import Client
from suds.cache import ObjectCache
from suds.transport.http import HttpAuthenticated


class CacheQueryError(Exception):
    pass


class ProxyObject(dict):
    def __init__(self, *args, **kwargs):
        super(ProxyObject, self).__init__(*args, **kwargs)
        self.__dict__ = self


class CacheSOAPQuery:
    """
    Класс выполняющий запросы к базе данных через SOAP
        Если произошла ошибка выбрасывает исключение CacheQueryError
    """
    def __nullstate(self):
        self.clients = {}
        self.data = []          # ответ запроса таблица
        self.columns = []       # список полей
        self._result = None      # Первое поле первой строки ответа

    def __init__(self, connection_param, queries, cache_coding='cp1251', always_new_connect=False):
        self.user = connection_param.get("user", "_SYSTEM")
        self.password = connection_param.get("password", "_SYS")
        self.queries = queries
        self.logger = logging.getLogger("cachequery")
        self.qms_answer_logger = logging.getLogger("qms_answers")
        # 'http://10.1.100.5:57772/csp/skcqms/DeepSeeExtract.Query.cls?wsdl'
        self.connection_string = 'http://' + connection_param['host'] + ':' + \
                                 connection_param['wsdl_port'] + '/csp/' + \
                                 connection_param['namespace'] + '/' + '{class_name}.cls?wsdl'
        self.always_new_connect = always_new_connect
        self.cache_coding = cache_coding
        self.__nullstate()

    @property
    def result(self):
        """
        :return:
        Возвращает первое поле первой строки ответа
        Для методов, которые возвращают один ответ
        """
        if self._result:
            return self._result
        else:
            return self.data[0][0]

    def get_columns(self):
        """
        Возвращает список имен стобцов
        """
        return self.columns

    def _get_client(self, class_name):
        """
        Возвращает строку соединения wsdl для запроса
        """
        if class_name in self.clients:
            if not self.always_new_connect:
                return self.clients[class_name]
        oc = ObjectCache(minutes=60, seconds=1)
        auth = HttpAuthenticated(username=self.user, password=self.password)
        self.clients[class_name] = Client(self.connection_string.format(class_name=class_name),
                                          username=self.user,
                                          password=self.password,
                                          cache=oc,
                                          transport=auth)
        return self.clients[class_name]

    @staticmethod
    def _get_simple_diffgram(diffgram, columns):
        return list(map(lambda u: diffgram[u] if u in diffgram else "", columns))

    @staticmethod
    def _get_diffgram(query_name, diffgram, columns):
        method_name = query_name
        diffgr_path = ["%s_DataSet" % method_name, method_name]
        dg = reduce(lambda res, u: res[u], diffgr_path, diffgram)
        if isinstance(dg, list):
            return list(map(lambda u: CacheSOAPQuery._get_simple_diffgram(u, columns), dg))
        else:
            return [CacheSOAPQuery._get_simple_diffgram(dg, columns)]

    def execute_query(self, query_name, *params):
        assert query_name in self.queries
        self.__nullstate()
        self.logger.debug('Execute query ' + query_name + str(params))
        try:
            client = self._get_client(self.queries[query_name]['class'])
        except Exception as err:
            self.logger.error(err)
            raise CacheQueryError("Connection error")
        try:
            # Если вызов метода класса а не запроса
            if self.queries[query_name].get('class_method'):
                func = getattr(client.service, self.queries[query_name]['class_method'])
                self._result = func(*params)
                self.logger.debug(str(self._result))
                return self._result
            func = getattr(client.service, self.queries[query_name]['query'])
            results = func(*params)
            return self
        except Exception as err:
            self.logger.error(err)
            raise CacheQueryError("Execute query error")

        # Обработка ответа с набором данных
        element_name, complex_type_name = "element", "complexType"
        sch_path = [element_name, complex_type_name, "choice", element_name, complex_type_name, "sequence", element_name]
        diffgram = results['diffgram']
        columns = reduce(lambda res, u: res[u], sch_path, results['schema'])
        if isinstance(columns, list):
            columns = list(map(lambda u: u['_name'], columns))
        else:
            columns = [columns['_name']]
        self.columns = columns
        try:
            data = self._get_diffgram(self.queries[query_name]['query'], diffgram, columns)
        except Exception as err:
            self.logger.error(err)
            raise CacheQueryError("Execute query error")
        self.data = list(data)
        self._result = data[0][0]
        self.qms_answer_logger("\n".join(list(map(lambda u: "| ".join(map(lambda q: str(q) if q else '', u)), data))))

    def fetch_all(self):
        return self.data

    def results(self):
        """
        Итератор по результатам запроса
        """
        return iter(self.data)

    def get_proxy_objects_list(self):
        """
        Возвращает список словарей
        Ключи - поля
        """
        return [ProxyObject(zip(self.columns, line)) for line in self.results()]


class CacheODBCQuery:
    """
    Класс выполняющий запросы к базе данных по ODBC.
    Если произошла ошибка выбрасывает исключение CacheQueryError
    """
    def __nullstate__(self):
        self.query = None
        self.good = True
        self._result = None  # Первое поле первой строки ответа

    def __init__(self, connection_param, queries, cache_coding='cp1251', always_new_connect=False):
        """
        connection_param - словарь настроек
               ключи: user,password,host,port,wsdl_port
        queries - словарь местоположений запросов в QMS
        Пример словаря:
        'LoadMKB': {
                            'class': 'DeepSeeExtract.Query',
                            'query': 'MKB'
                },
        cache_coding - кодировка базы данных cache
        always_new_connect - Если true при каждом запросе создавать новое соединение
        """
        self.user = connection_param.get("user", "_SYSTEM")
        self.password = connection_param.get("password", "_SYS")
        self.host = connection_param.get("host", "localhost")
        self.port = connection_param.get("port", "1972")
        self.namespace = connection_param.get("namespace", "USER")
        self.queries = queries
        self.logger = logging.getLogger("cachequery")
        self.qms_answer_logger = logging.getLogger("qms_answers")
        self.cache_coding = cache_coding
        self.always_new_connect = always_new_connect
        self.url = self.host + "[" + self.port + "]:" + self.namespace
        self.database = None
        self.conn = None
        self.__nullstate__()
        self._make_connection()

    @property
    def result(self):
        """
        :return:
        Возвращает первое поле первой строки ответа
        Для методов, которые возвращают один ответ
        """
        if self._result:
            return self._result
        else:
            try:
                return self._fetch()[0]
            except AttributeError:
                return None

    def _make_connection(self):
        del self.conn
        self.good = True
        try:
            self.conn = intersys.pythonbind3.connection()
            self.conn.connect_now(self.url, self.user, self.password, None)
            self.database = intersys.pythonbind3.database(self.conn)
            self.logger.debug('Установлено соединение с базой')
        except intersys.pythonbind3.cache_exception as err:
            self.logger.error(err)
            self.good = False
            raise CacheQueryError("Connection error")

    def execute_query(self, query_name, *params):
        """
        query_name - имя запроса из queries_location
        *params - параметры запроса
        """
        assert query_name in self.queries
        self.__nullstate__()
        self.logger.debug('Execute query ' + query_name + str(params))
        # Если вызов метода класса а не запроса
        if self.queries[query_name].get('class_method'):
            self._result = self._execute_class_method(query_name, *params)
            return self._result
        try:
            # create a query
            if self.always_new_connect:
                self._make_connection()
            self.query = intersys.pythonbind3.query(self.database)
            self.query.prepare_class(self.queries[query_name]['class'],
                                     self.queries[query_name]['query'])
            # Установка в цикле всех параметров запроса
            for paramIndex in range(len(params)):
                if params[paramIndex]:
                    param = str(params[paramIndex])
                    self.query.set_par(paramIndex+1, param)
            self.query.execute()
            return self
        except (intersys.pythonbind3.cache_exception, KeyError) as err:
            self.logger.error(err)
            self.good = False
            raise CacheQueryError("Execute query error")

    def _execute_class_method(self, query_name, *params):
        try:
            params_list = list(map(lambda param: str(param).encode(self.cache_coding), params))
            answer = self.database.run_class_method(self.queries[query_name]['class'],
                                           self.queries[query_name]['class_method'],
                                           params_list)
            if isinstance(answer, bytes):
                return answer.decode(self.cache_coding)
            return answer
        except (intersys.pythonbind3.cache_exception, KeyError) as err:
            self.logger.error(err)
            self.good = False
            raise CacheQueryError("Execute query error")

    def get_columns(self):
        return [self.query.col_name(i) for i in range(1, self.query.num_cols()+1)]

    def _fetch(self):
        lst = self.query.fetch([None])
        if len(lst) == 0:
            return []
        else:
            self.qms_answer_logger.debug("| ".join(list(map(str, lst))))
            if self._result is None:
                self._result = lst[0]
        return lst

    def fetch_all(self):
        """
        Возвращает список всех строк ответа
        """
        return [one_row for one_row in self.results()]

    def results(self):
        """
        Возвращает  итератор по результатам запроса
        """
        if not self.good:
            return []
        return iter(self._fetch, [])

    def get_proxy_objects_list(self):
        """
        Возвращает список словарей
        Ключи - поля
        """
        columns = self.get_columns()
        return [ProxyObject(zip(columns, line)) for line in self.results()]
