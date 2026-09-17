from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.generator.service import create_material_content
from apps.materials.models import Material
from apps.subjects.models import Grade, MaterialType, Subject


class CreateMaterialForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), label="Класс")
    subject = forms.ModelChoiceField(queryset=Subject.objects.filter(is_active=True), label="Предмет")
    material_type = forms.ModelChoiceField(queryset=MaterialType.objects.filter(is_active=True), label="Тип материала")

    topic = forms.CharField(max_length=500, label="Тема урока", widget=forms.TextInput(attrs={"placeholder": "Например: Древняя Греция"}))

    duration = forms.IntegerField(required=False, min_value=5, max_value=90, label="Длительность (мин)", initial=45)
    lesson_type = forms.ChoiceField(
        required=False,
        label="Тип урока",
        choices=[
            ("", "—"),
            ("изучение нового материала", "изучение нового материала"),
            ("повторение", "повторение"),
            ("практическое занятие", "практическое занятие"),
            ("контроль знаний", "контроль знаний"),
            ("комбинированный урок", "комбинированный урок"),
        ],
    )
    questions = forms.IntegerField(required=False, min_value=1, max_value=50, label="Количество вопросов", initial=5)
    difficulty = forms.ChoiceField(
        required=False,
        label="Сложность",
        choices=[
            ("easy", "лёгкая"),
            ("medium", "средняя"),
            ("hard", "сложная"),
        ],
    )
    slides = forms.IntegerField(required=False, min_value=3, max_value=50, label="Количество слайдов", initial=7)
    style = forms.ChoiceField(
        required=False,
        label="Стиль",
        choices=[
            ("минималистичный", "минималистичный"),
            ("яркий", "яркий"),
            ("академический", "академический"),
        ],
    )

    blocks = forms.MultipleChoiceField(
        required=False,
        label="Дополнительные блоки",
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ("цели урока", "цели урока"),
            ("планируемые результаты", "планируемые результаты"),
            ("оборудование", "оборудование"),
            ("ход урока", "ход урока"),
            ("практическое задание", "практическое задание"),
            ("вопросы ученикам", "вопросы ученикам"),
            ("домашнее задание", "домашнее задание"),
            ("рефлексия", "рефлексия"),
        ],
    )

    def get_params(self) -> dict:
        data = self.cleaned_data.copy()
        grade = data.pop("grade")
        data["grade"] = grade.number
        material_type = data.pop("material_type")
        data["_material_type"] = material_type
        data["_grade_obj"] = grade
        return data


@login_required
def home(request):
    form = CreateMaterialForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        params = form.get_params()
        material_type = params.pop("_material_type")
        grade_obj = params.pop("_grade_obj")

        content = create_material_content(material_type, params)
        material = Material.objects.create(
            user=request.user,
            grade=grade_obj,
            subject=form.cleaned_data["subject"],
            material_type=material_type,
            title=params.get("topic") or "Материал",
            contents=content,
            settings={
                k: v
                for k, v in params.items()
                if k not in ("grade", "subject") and v
            },
        )
        return redirect("materials:detail", pk=material.pk)

    return render(request, "generator/home.html", {"form": form})