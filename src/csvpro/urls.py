from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from csvpro.forms import LoginForm
from csvpro.views import (CSVGenerateView, DataSchemaCreateView,
                          DataSchemaListView, DataSchemaUpdateView,
                          DeleteSchemaView)

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html", authentication_form=LoginForm), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", DataSchemaListView.as_view(), name="csv_index"),
    path("new/", DataSchemaCreateView.as_view(), name="new_schema"),
    path("delete/<int:pk>/", DeleteSchemaView.as_view(), name="delete_schema"),
    path("update/<int:pk>/", DataSchemaUpdateView.as_view(), name="update_schema"),
    path("csv/", CSVGenerateView.as_view(), name="generate_csv"),
]
