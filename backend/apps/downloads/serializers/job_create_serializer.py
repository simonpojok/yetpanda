"""POST /v1/jobs request body."""

from rest_framework import serializers

from apps.extraction.options.mp3_options import MP3_BITRATES

from ..models import MediaKindChoice, SubtitleModeChoice

VIDEO_HEIGHTS = (144, 240, 360, 480, 720, 1080, 1440, 2160)


class JobCreateSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=2048, trim_whitespace=True)
    kind = serializers.ChoiceField(choices=MediaKindChoice.choices)
    height = serializers.ChoiceField(choices=VIDEO_HEIGHTS, required=False)
    audio_bitrate_kbps = serializers.ChoiceField(choices=MP3_BITRATES, required=False)
    passthrough = serializers.BooleanField(required=False, default=False)
    subtitle_mode = serializers.ChoiceField(
        choices=SubtitleModeChoice.choices, required=False, default=SubtitleModeChoice.NONE
    )
    subtitle_langs = serializers.ListField(
        child=serializers.CharField(max_length=16), required=False, default=list
    )

    def validate(self, attrs):
        if attrs["kind"] == MediaKindChoice.VIDEO and not attrs.get("height"):
            raise serializers.ValidationError({"height": "Choose a quality."})
        if (
            attrs["kind"] == MediaKindChoice.AUDIO
            and not attrs.get("passthrough")
            and not attrs.get("audio_bitrate_kbps")
        ):
            raise serializers.ValidationError({"audio_bitrate_kbps": "Choose a bitrate."})
        if attrs.get("subtitle_mode") != SubtitleModeChoice.NONE and not attrs.get(
            "subtitle_langs"
        ):
            raise serializers.ValidationError(
                {"subtitle_langs": "Choose at least one language."}
            )
        return attrs

    def to_spec(self) -> dict:
        data = self.validated_data
        return {
            "height": data.get("height"),
            "audio_bitrate_kbps": data.get("audio_bitrate_kbps"),
            "passthrough": data.get("passthrough", False),
            "subtitle_mode": data.get("subtitle_mode", SubtitleModeChoice.NONE),
            "subtitle_langs": data.get("subtitle_langs", []),
        }
