from rest_framework import serializers

class AsyncSearchSerializer(serializers.Serializer):
    callback_url = serializers.CharField(required=True)
    query = serializers.CharField(required=True)
    engine = serializers.CharField(default="gpt-3.5-turbo")
    category_slug = serializers.CharField(required=True)
