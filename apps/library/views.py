from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.exports.exporter import generate_docx, generate_pdf
from apps.materials.models import Material
from apps.subjects.models import Grade, MaterialType, Subject


def library_list(request):
    materials = Material.objects.filter(is_published=True).select_related(
        "subject", "grade", "material_type", "user"
    )

    grade = request.GET.get("grade", "")
    subject = request.GET.get("subject", "")
    mtype = request.GET.get("type", "")
    if grade:
        materials = materials.filter(grade_id=grade)
    if subject:
        materials = materials.filter(subject_id=subject)
    if mtype:
        materials = materials.filter(material_type_id=mtype)

    return render(
        request,
        "library/list.html",
        {
            "materials": materials,
            "grades": Grade.objects.all(),
            "subjects": Subject.objects.filter(is_active=True),
            "types": MaterialType.objects.filter(is_active=True),
            "selected": {"grade": grade, "subject": subject, "type": mtype},
        },
    )


@login_required
def library_download(request, pk, fmt):
    """Скачивание опубликованного материала из библиотеки (не владельца)."""
    material = get_object_or_404(Material, pk=pk, is_published=True)
    html = material.contents.get("html", "") if isinstance(material.contents, dict) else material.contents

    filename = material.title.replace(" ", "_").replace("/", "_")
    if fmt == "docx":
        buf = generate_docx(html, material.title)
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ext = "docx"
    elif fmt == "pdf":
        buf = generate_pdf(html, material.title)
        content_type = "application/pdf"
        ext = "pdf"
    else:
        return HttpResponse("Неизвестный формат", status=400)

    response = HttpResponse(buf.read(), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}.{ext}"'
    return response