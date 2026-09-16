"""POST /v1/batches request body: one preference for the whole playlist."""

from rest_framework import serializers

from .job_create_serializer import JobCreateSerializer


class BatchCreateSerializer(JobCreateSerializer):
    item_indexes = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=False,
        allow_empty=False,
        help_text="Omit to take every available item.",
    )
