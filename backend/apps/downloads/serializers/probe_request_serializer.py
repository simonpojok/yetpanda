"""POST /v1/probe request body."""

from rest_framework import serializers


class ProbeRequestSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=2048, trim_whitespace=True)
