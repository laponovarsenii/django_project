from django.utils import timezone
from rest_framework import serializers

from my_django_app.models import Task, SubTask, Category


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'categories',
            'status',
            'deadline',
            'created_at',
            'created_date',
            'owner',   # добавили
        ]
        read_only_fields = ['created_at', 'created_date', 'owner']
    # ...

    def validate_deadline(self, value):
        if value is not None and value < timezone.now():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = [
            'id',
            'title',
            'description',
            'task',
            'status',
            'deadline',
            'created_at',
        ]
        read_only_fields = ['created_at']


class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = [
            'id',
            'title',
            'description',
            'task',
            'status',
            'deadline',
            'created_at',
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_deleted', 'deleted_at']
        read_only_fields = ['is_deleted', 'deleted_at']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def create(self, validated_data):
        name = validated_data.get('name')
        if Category.all_objects.filter(name=name, is_deleted=False).exists():
            raise serializers.ValidationError({
                'name': 'Category with this name already exists.'
            })
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        if Category.all_objects.filter(name=name, is_deleted=False).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({
                'name': 'Category with this name already exists.'
            })
        return super().update(instance, validated_data)


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'categories',
            'status',
            'deadline',
            'created_at',
            'created_date',
            'subtasks',
            'owner',
        ]