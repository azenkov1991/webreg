from config.settings.common import CONSTANCE_CONFIG

CONSTANCE_CONFIG.update({
    'PBSEARCH_ERROR': (''.join((
        'Ошибка! Пациент не найден в базе выбранного города.</br>',
        'Возможные причины:',
        '<ul>',
        '<li>Вы не прикреплены к СКЦ или КБ №42;</li>',
        '<li>Вы недавно поменяли полис ОМС. Обратитесь в регистратуру СКЦ или КБ №42;</li>',
        '</ul>',
        'Для дополнительной консультации обратитесь в call-центр.')
    ), 'Ошибка поиска пациента'),

    'TIMETABLE_DAY': (7, 'Количество дней в расписании'),
})

# общий пользователь для записи на прием пациентов
PATIENT_WRITER_USER = 'patient_writer'

# общий профиль для проекта записи на прием
PATIENT_WRITER_PROFILE = "patient_writer"
