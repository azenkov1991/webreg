from catalogs.models import *
from qmsmodule.qmsfunctions import *

def load_mkb(self, cache_settings):
    """
    Загрузка справочников МКБ из qms
    """
    query = QMS(cache_settings).query
    for level in range(1, 5):
        query.execute_query('LoadMKB', level)
        for service_fields_list in query.results():
            code = service_fields_list[0]
            name = service_fields_list[1]
            is_finished = (level >= 4)
            if code is not None and name is not None:
                try:
                    mkb_obj = MKBDiagnos.objects.get(code=code)
                except MKBDiagnos.DoesNotExist:
                    mkb_obj = MKBDiagnos(code=code, name=name, is_finished=is_finished, level=level)
                else:
                    mkb_obj.is_finished = is_finished
                    mkb_obj.level = level
                    mkb_obj.name = name
                mkb_obj.save()
