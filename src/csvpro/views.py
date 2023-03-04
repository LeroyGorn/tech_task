import csv
import os

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import (HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.views import generic

from csvpro.csv_generator import generate_csv
from csvpro.forms import ColumnFormset, SchemaForm
from csvpro.models import DataColumn, DataSchema


class DataSchemaListView(generic.ListView):
    template_name = "index.html"
    context_object_name = "schemas"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return DataSchema.objects.filter(owner=self.request.user).order_by("-created")


class DataSchemaCreateView(generic.CreateView):
    form_class = SchemaForm
    success_url = "/"
    template_name = "create_schema.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DataSchemaCreateView, self).get_context_data(**kwargs)
        context["formset"] = ColumnFormset()
        context["schema_form"] = SchemaForm()
        return context

    def post(self, request, *args, **kwargs):
        formset = ColumnFormset(request.POST)
        schema_form = SchemaForm(request.POST)
        if formset.is_valid() and schema_form.is_valid():
            return self.form_valid(schema_form, formset=formset)
        return super(DataSchemaCreateView, self).post(self, request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        with transaction.atomic():
            schema = form.save(commit=False)
            schema.owner = self.request.user
            schema.save()
            schema = form.save()
            formset = kwargs.get("formset")
            for column_form in formset:
                instance = DataColumn.objects.create(
                    columns=schema,
                    column_type=column_form.cleaned_data["column_type"],
                    column_name=column_form.cleaned_data["column_name"],
                    order=column_form.cleaned_data["order"],
                    from_value=column_form.cleaned_data.get("from_value"),
                    to_value=column_form.cleaned_data.get("to_value"),
                )
                instance.save()
        return redirect("csv_index")


class DataSchemaUpdateView(generic.UpdateView):
    model = DataSchema
    form_class = SchemaForm
    template_name = "create_schema.html"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(DataSchema, id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        scheme = self.get_object()
        initial_data = [
            {
                "id": x.id,
                "column_type": x.column_type,
                "column_name": x.column_name,
                "order": x.order,
                "columns": scheme,
                "from_value": x.from_value,
                "to_value": x.to_value,
            }
            for x in scheme.data_column.all()
        ]
        formset = ColumnFormset(request.POST, initial=initial_data)
        schema_form = SchemaForm(request.POST, instance=self.get_object())
        if formset.is_valid() and schema_form.is_valid():
            return self.form_valid(schema_form, formset=formset)
        return super(DataSchemaUpdateView, self).post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DataSchemaUpdateView, self).get_context_data(**kwargs)
        scheme = self.get_object()
        initial_data = [
            {
                "id": x.id,
                "column_type": x.column_type,
                "column_name": x.column_name,
                "order": x.order,
                "columns": scheme,
                "from_value": x.from_value,
                "to_value": x.to_value,
            }
            for x in scheme.data_column.all()
        ]

        context["formset"] = ColumnFormset(initial=initial_data)
        context["schema_form"] = SchemaForm(instance=self.get_object())
        return context

    def form_valid(self, form, **kwargs):
        with transaction.atomic():
            schema = form.save(commit=False)
            schema.owner = self.request.user
            schema.status = DataSchema.StatusChoices.generated
            schema.save()
            schema.data_column.all().delete()
            formset = kwargs.get("formset")
            for column_form in formset:
                instance = DataColumn.objects.create(
                    columns=schema,
                    column_type=column_form.cleaned_data["column_type"],
                    column_name=column_form.cleaned_data["column_name"],
                    order=column_form.cleaned_data["order"],
                    from_value=column_form.cleaned_data.get("from_value"),
                    to_value=column_form.cleaned_data.get("to_value"),
                )
                instance.save()
        return redirect("csv_index")


class DeleteSchemaView(generic.DeleteView):
    template_name = "delete_schema.html"
    context_object_name = "schema"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(DataSchema, id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        if self.request.POST.get("confirm_delete"):
            schema = self.get_object()
            schema.delete()
            return HttpResponseRedirect(self.success_url)
        elif self.request.POST.get("cancel"):
            return HttpResponseRedirect(self.success_url)
        else:
            return self.get_object()


class CSVResponseMixin:
    def render_to_response(self, context, **response_kwargs):
        req = self.request.GET.copy()
        if req.get("csv", "") == "true" and req.get("file_id"):
            schema = get_object_or_404(DataSchema, pk=req.get("file_id"))
            path = schema.get_file_link()
            file_path = settings.MEDIA_ROOT + path
            if os.path.exists(file_path):
                with open(file_path, "rb") as fh:
                    response = HttpResponse(fh.read(), content_type="text/csv")
                    response["Content-Disposition"] = 'attachment; filename="%s"' % schema.filename
                    return response
        elif req.get("csv", "") == "false" and req.get("file_id"):
            schema = get_object_or_404(DataSchema, pk=req.get("file_id"))
            filepath = os.path.join(settings.MEDIA_ROOT, "files", f"report{schema.id}_{schema.updated}.csv")
            with open(filepath, "w") as csvfile:
                query = schema.data_column.all().order_by("order")
                file_headers = query.values_list("column_name", flat=True)
                range_values = query.values("from_value", "to_value", "column_type")
                writer = csv.writer(
                    csvfile,
                    delimiter=schema.column_separator,
                    quotechar=schema.string_character,
                    quoting=csv.QUOTE_NONNUMERIC,
                )
                writer.writerow(file_headers)
                for n in range(1, int(req.get("rows"))):
                    writer.writerow(generate_csv(range_values=range_values))

                schema.file.name = filepath
                schema.filename = os.path.basename(csvfile.name)
                schema.status = DataSchema.StatusChoices.ready
                schema.save()
                template = loader.get_template("table_ajax.html")
                content = template.render(context, self.request)
                return JsonResponse({"status": "success", "content": content})
        return super(CSVResponseMixin, self).render_to_response(context, **response_kwargs)


class CSVGenerateView(CSVResponseMixin, generic.TemplateView):
    template_name = "generate_csv.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CSVGenerateView, self).get_context_data(**kwargs)
        context["schema_columns"] = DataColumn.objects.filter(columns__id=1)
        context["schemas"] = DataSchema.objects.filter(owner=self.request.user).order_by("updated")
        return context
