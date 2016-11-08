from catalogs.models import *
from qmsmodule.qmsfunctions import *


def load_mkb(self, cache_settings):
    """
    Загрузка справочников МКБ из qms
    """
    query = QMS(cache_settings).query
    for level in range(1, 5):
        query.execute_query('LoadMKB', level)
        for mkb in query.get_proxy_objects_list():
            code = mkb.code
            name = mkb.name
            parent = mkb.parent
            try:
                parent_obj = MKBDiagnos.objects.get(code=parent)
            except MKBDiagnos.DoesNotExist:
                parent_obj = None
            is_finished = (level >= 4)
            if code and name:
                try:
                    mkb_obj = MKBDiagnos.objects.get(code=code)
                except MKBDiagnos.DoesNotExist:
                    mkb_obj = MKBDiagnos(code=code)
                mkb_obj.is_finished = is_finished
                mkb_obj.level = level
                mkb_obj.name = name
                mkb_obj.parent = parent_obj
                mkb_obj.save()
