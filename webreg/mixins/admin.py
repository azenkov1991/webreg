

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
    cls.get_queryset = get_queryset
    return cls

