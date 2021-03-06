from rest_framework import serializers

from openwisp_users.api.mixins import FilterSerializerByOrgManaged
from openwisp_utils.api.serializers import ValidatedModelSerializer

from ..swapper import load_model

BatchUpgradeOperation = load_model('BatchUpgradeOperation')
Build = load_model('Build')
Category = load_model('Category')
FirmwareImage = load_model('FirmwareImage')
UpgradeOperation = load_model('UpgradeOperation')


class BaseMeta:
    read_only_fields = ['created', 'modified']


class BaseSerializer(FilterSerializerByOrgManaged, ValidatedModelSerializer):
    pass


class CategorySerializer(BaseSerializer):
    class Meta(BaseMeta):
        model = Category
        fields = '__all__'


class CategoryRelationSerializer(BaseSerializer):
    class Meta:
        model = Category
        fields = ['name', 'organization']


class FirmwareImageSerializer(BaseSerializer):
    def validate(self, data):
        data['build'] = self.context['view'].get_parent_queryset().get()
        return super().validate(data)

    class Meta(BaseMeta):
        model = FirmwareImage
        fields = '__all__'
        read_only_fields = BaseMeta.read_only_fields + ['build']


class BuildSerializer(BaseSerializer):
    category_relation = CategoryRelationSerializer(read_only=True, source='category')

    class Meta(BaseMeta):
        model = Build
        fields = '__all__'


class UpgradeOperationSerializer(BaseSerializer):
    class Meta:
        model = UpgradeOperation
        exclude = ['batch']


class BatchUpgradeOperationListSerializer(BaseSerializer):
    build = BuildSerializer(read_only=True)

    class Meta:
        model = BatchUpgradeOperation
        fields = '__all__'


class BatchUpgradeOperationSerializer(BatchUpgradeOperationListSerializer):
    progress_report = serializers.CharField(max_length=200)
    success_rate = serializers.IntegerField(read_only=True)
    failed_rate = serializers.IntegerField(read_only=True)
    aborted_rate = serializers.IntegerField(read_only=True)
    upgradeoperations = UpgradeOperationSerializer(
        read_only=True, source='upgradeoperation_set', many=True
    )

    class Meta:
        model = BatchUpgradeOperation
        fields = '__all__'
