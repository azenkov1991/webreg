from django.contrib import admin


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.
    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    Source: https://gist.github.com/aaugustin/1388243
    """
    actions = None

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return (request.method in ['GET', 'HEAD'] and
                super().has_change_permission(request, obj))

    def has_delete_permission(self, request, obj=None):
        return False


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



