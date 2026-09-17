"""REST API (раздел 14 ТЗ) для классов, предметов, типов и материалов."""

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.generator.service import create_material_content
from apps.subjects.models import Grade, MaterialType, Subject

from .models import Material


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "number", "name"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "slug", "is_active"]


class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = ["id", "name", "slug", "structure", "variables", "is_active"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = [
            "id",
            "title",
            "grade",
            "subject",
            "material_type",
            "contents",
            "settings",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialGenerateSerializer(serializers.Serializer):
    grade = serializers.IntegerField()
    subject = serializers.SlugField()
    type = serializers.SlugField(required=False, default="lesson_plan")
    topic = serializers.CharField()
    duration = serializers.IntegerField(required=False, default=45)
    lesson_type = serializers.CharField(required=False, default="изучение нового материала")
    questions = serializers.IntegerField(required=False)
    difficulty = serializers.CharField(required=False)
    slides = serializers.IntegerField(required=False)
    style = serializers.CharField(required=False)
    blocks = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"


class MaterialTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaterialType.objects.filter(is_active=True)
    serializer_class = MaterialTypeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"


class MaterialViewSet(viewsets.ModelViewSet):
    """Персональные материалы текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Material.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return MaterialSerializer

    @action(detail=False, methods=["post"], serializer_class=MaterialGenerateSerializer)
    def generate(self, request):
        serializer = MaterialGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grade = Grade.objects.get_or_create(number=data["grade"])[0]
        subject = Subject.objects.get(slug=data["subject"])
        material_type = MaterialType.objects.get(slug=data["type"])

        params = {
            "grade": data["grade"],
            "subject": subject.name,
            "topic": data["topic"],
            "duration": data.get("duration"),
            "lesson_type": data.get("lesson_type"),
            "questions": data.get("questions"),
            "difficulty": data.get("difficulty"),
            "slides": data.get("slides"),
            "style": data.get("style"),
            "blocks": data.get("blocks", []),
        }

        try:
            content = create_material_content(material_type, params)
        except Exception as exc:
            return Response(
                {"error": f"Ошибка генерации: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        material = Material.objects.create(
            user=request.user,
            grade=grade,
            subject=subject,
            material_type=material_type,
            title=data["topic"],
            contents=content,
            settings={k: v for k, v in params.items() if v},
        )
        return Response(
            MaterialSerializer(material).data, status=status.HTTP_201_CREATED
        )