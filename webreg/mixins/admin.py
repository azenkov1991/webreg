def undelete_selected(self, request, queryset):
    assert hasattr(queryset, 'undelete')
    queryset.undelete()
undelete_selected.short_description = "Сделать активными выбранные %(verbose_name_plural)s."


def safe_delete_selected(self, request, queryset):
    assert hasattr(queryset, 'safe_delete')
    queryset.safe_delete()
safe_delete_selected.short_description = "Сделать неативными выбранные %(verbose_name_plural)s."


def safe_delete_mixin_admin(cls):
    """
    Декоратор для класса ModelAdmin.
    """
    def get_queryset(self, request):
        # use our manager, rather than the default one
        qs = self.model.all_objects.get_queryset()
        # we need this from the superclass method
        ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    cls.list_display += ('active',)
    cls.list_filter = ('deleted',) + cls.list_filter
    cls.get_queryset = get_queryset
    cls.actions = [undelete_selected, safe_delete_selected]
    return cls

