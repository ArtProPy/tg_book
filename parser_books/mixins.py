class AdminListPrefetchRelatedMixin:
    list_prefetch_related = []

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        for field in self.list_prefetch_related:
            queryset = queryset.prefetch_related(field)
        return queryset
