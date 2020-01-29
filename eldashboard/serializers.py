from rest_framework import serializers
from rest_framework import generics
#from django.core import serializers
from .models import Sample
from eldashboard.models import Clients


class DropDownSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50)

class SampleSerializer(serializers.ModelSerializer):


    client = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
     )

    class Meta:
        model = Sample
        fields = ('__all__')



"""
NESTED RELATIONSHIPS
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['order', 'title', 'duration']

class AlbumSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']
"""

