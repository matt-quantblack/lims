from rest_framework import serializers
from rest_framework import generics
#from django.core import serializers
from .models import *


def serialize_jobsample(jobsample):
    sample = {'id': jobsample.id, 'sample': {'name': jobsample.sample.name,
                                             'id': jobsample.sample.id,
                                             'client': jobsample.sample.client,
                                             'clientref': jobsample.sample.clientref,
                                             'batch': jobsample.sample.batch}}

    alltests = SampleTests.objects.filter(jobsample_id=jobsample.id).all()
    sample["tests"] = []
    for t in alltests:
        sample["tests"].append({'name': t.test.name, 'tmnumber': t.test.tmnumber})

    return sample


class DropDownSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=50)

class TestMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestMethods
        fields = ('__all__')

class JobReportSerializer(serializers.ModelSerializer):

    job = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id'
    )

    class Meta:
        model = JobReports
        fields = ('__all__')

class SampleSerializer(serializers.ModelSerializer):


    client = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
     )

    class Meta:
        model = Sample
        fields = ('__all__')

class JobSampleListSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return "#{} {}".format(obj.sample.id, obj.sample.name)

    class Meta:
        model = JobSample
        fields = ['name']

class JobListSerializer(serializers.ModelSerializer):

    client = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
     )

    jobsamples = JobSampleListSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'client', 'jobsamples', 'status']

class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Clients
        fields = ('__all__')

class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contacts
        fields = ('__all__')

class ReportTemplateSerializer(serializers.ModelSerializer):
    report_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = ReportTemplates
        fields = ('__all__')

class NotificationGroupSerializer(serializers.ModelSerializer):
    client = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id'
    )

    class Meta:
        model = NotificationGroups
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

