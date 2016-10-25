QMS_QUERIES = {
                'SearchPatient': {
                                 'class': 'User.Query',
                                 'query': 'PBSearch'
                },
                'PatientDetail': {
                                 'class': 'User.Query',
                                 'query': 'PatientDetail'
                },
                'CreatePatient': {
                                 'class': 'User.Query',
                                 'class_method': 'CrePatient'
                },
                'AvailSpec': {
                    'class': 'User.QueryCatalog',
                    'query': 'AvailSpec'
                },
                'GetAllDoctors': {
                    'class': 'User.QueryCatalog',
                    'query': 'Doctors'
                },
                'CreatePolis': {
                    'class': 'User.Query',
                    'query': 'CrePolisQuery'
                },
                'CancelAppointment': {
                                 'class': 'User.QueryCatalog',
                                 'query': 'cancel1860'
                },
                'Create174': {
                              'class': 'User.Query',
                              'query': 'Cre174'
                },
                'Create186': {
                              'class': 'User.Query',
                              'query': 'Cre186'
                },
                'Create1860Schedule': {
                                        'class': 'User.Query',
                                        'query': 'Cre1860schedule'
                },
                'Create1860': {
                              'class': 'User.Query',
                              'query': 'Cre1860'
                },
                'LoadOKMU': {
                            'class': 'User.QueryCatalog',
                            'query': 'OKMU'
                },
    }
