from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models


class Cell(models.Model):
    date = models.DateField(
        verbose_name="Дата приема", db_index=True
    )
    time_start = models.TimeField(
        verbose_name="Время приема"
    )
    time_end = models.TimeField(
        verbose_name="Окончание приема"
    )
    specialist = models.ForeignKey(
        'main.Specialist', verbose_name="Специалист",
        db_index=True, null=True, on_delete=models.SET_NULL
    )
    cabinet = models.ForeignKey(
        'main.Cabinet', verbose_name="Кабинет", null=True, blank=True
    )
    performing_services = models.ManyToManyField(
        "catalogs.OKMUService", verbose_name="Выполняемые услуги", blank=True
    )
    slot_type = models.ForeignKey(
        'main.SlotType', verbose_name="Тип слота",
        null=True, blank=True, on_delete=models.SET_NULL
    )
    free  = models.BooleanField(
        verbose_name="Свободна", default=True
    )

    @property
    def time_str(self):
        return '%s-%s' % (self.time_start.strftime('%H:%M'), self.time_end.strftime('%H:%M'))

    def __str__(self):
        return self.date.strftime("%d.%m.%Y") + " " + self.time_start.strftime("%H:%M") + "-" +\
               self.time_end.strftime("%H:%M") + " " + str(self.cabinet) + " " + str(self.specialist)

    def full_clean(self, exclude=None, validate_unique=True):
        try:
            super(Cell, self).full_clean(None, validate_unique)
        except ValidationError as e:
            raise e
        else:
            Cell.save_cell_validation(self)

    @classmethod
    def save_cell_validation(cls, cell):
        today_cells = Cell.objects.filter(date=cell.date).exclude(id=cell.id)
        cells_in_cabinet = today_cells.filter(cabinet=cell.cabinet) if cell.cabinet else []
        # проверка пересечения ячеек в кабинете
        for other_cell in cells_in_cabinet:
            if cell.intersection(other_cell):
                raise ValidationError({NON_FIELD_ERRORS: ["Ячека пересекается с другой ячейкой по кабинету"]})
        # проверка пересечения ячеек у специалиста
        specialists_cells = today_cells.filter(specialist=cell.specialist)
        for other_cell in specialists_cells:
            if cell.intersection(other_cell):
                raise ValidationError("Ячека пересекается с другой ячейкой у специалиста")
        if cell.time_end <= cell.time_start:
            raise ValidationError({NON_FIELD_ERRORS: ["Время окончания приема должно быть больше времени начала"]})

    def intersection(self, cell):
        if (((cell.time_start <= self.time_start) and (self.time_start < cell.time_end)) or
                ((cell.time_start < self.time_end) and (self.time_end <= cell.time_end))):
            return True
        if (((self.time_start <= cell.time_start) and (cell.time_start < self.time_end)) or
                ((self.time_start < cell.time_end) and (cell.time_end <= self.time_end))):
            return True
        return False

    class Meta:
        app_label = 'main'
        verbose_name = "Ячейка"
        verbose_name_plural = "Ячейки"
        permissions = (
            ("view_timetable", "Разрешение на просмотр расписания"),
        )
