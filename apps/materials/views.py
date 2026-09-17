import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.ai.commands import run_ai_command
from apps.exports.exporter import generate_docx, generate_pdf
from apps.generator.service import create_material_content
from apps.subjects.models import MaterialType

from .models import Material

logger = logging.getLogger(__name__)


@login_required
def material_list(request):
    materials = Material.objects.filter(user=request.user)
    material_type = request.GET.get("type", "")
    if material_type:
        materials = materials.filter(material_type_id=material_type)
    return render(
        request,
        "materials/list.html",
        {
            "materials": materials,
            "types": MaterialType.objects.filter(
                id__in=request.user.materials.values_list("material_type_id", flat=True).distinct()
            ),
            "selected_type": material_type,
        },
    )


@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save":
            html = request.POST.get("content", "")
            title = request.POST.get("title", material.title)
            material.contents = {"html": html}
            material.title = title
            material.save()
            messages.success(request, "Материал сохранён.")
            return redirect("materials:detail", pk=material.pk)
        if action == "regenerate":
            content = create_material_content(material.material_type, material.settings)
            material.contents = content
            material.save()
            messages.success(request, "Материал сгенерирован заново.")
            return redirect("materials:detail", pk=material.pk)
        if action == "delete":
            material.delete()
            messages.success(request, "Материал удалён.")
            return redirect("materials:list")
        if action == "publish":
            html = request.POST.get("content", "")
            if html:
                material.contents = {"html": html}
            material.is_published = True
            material.save(update_fields=["contents", "is_published", "updated_at"])
            messages.success(request, "Материал опубликован в библиотеке.")
            return redirect("materials:detail", pk=material.pk)
        if action == "unpublish":
            html = request.POST.get("content", "")
            if html:
                material.contents = {"html": html}
            material.is_published = False
            material.save(update_fields=["contents", "is_published", "updated_at"])
            messages.success(request, "Материал скрыт из библиотеки.")
            return redirect("materials:detail", pk=material.pk)

    html = material.contents.get("html", "") if isinstance(material.contents, dict) else material.contents
    return render(request, "materials/editor.html", {"material": material, "content": html, "config": {"ai_base_url": None}})


@login_required
def material_duplicate(request, pk):
    material = get_object_or_404(Material, pk=pk, user=request.user)
    copy = material.duplicate_for(request.user)
    return redirect("materials:detail", pk=copy.pk)


@login_required
def material_export(request, pk, fmt):
    material = get_object_or_404(Material, pk=pk, user=request.user)
    html = material.contents.get("html", "") if isinstance(material.contents, dict) else material.contents
    title = material.title

    filename = f"{material.title}".replace(" ", "_").replace("/", "_")
    if fmt == "docx":
        buf = generate_docx(html, title)
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ext = "docx"
    elif fmt == "pdf":
        buf = generate_pdf(html, title)
        content_type = "application/pdf"
        ext = "pdf"
    else:
        return HttpResponse("Неизвестный формат", status=400)

    response = HttpResponse(buf.read(), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}.{ext}"'
    return response


@login_required
@require_POST
def material_ai_command(request, pk):
    """Применяет AI-команду к тексту материала (раздел 9 ТЗ)."""
    material = get_object_or_404(Material, pk=pk, user=request.user)
    command = request.POST.get("command", "")
    extra = request.POST.get("extra", "")
    content_html = request.POST.get("content", "")

    try:
        new_html = run_ai_command(content_html, command, extra)
        material.contents = {"html": new_html}
        material.save(update_fields=["contents", "updated_at"])
        return JsonResponse({"html": new_html})
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception as exc:
        logger.exception("AI-команда не выполнена")
        return JsonResponse({"error": str(exc)}, status=500)