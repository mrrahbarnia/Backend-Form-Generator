from django.urls import path

from . import apis

urlpatterns = [
    path('form-collection/', apis.CreateFormCollectionApi.as_view(), name='form_collection'),
    path('form-groups/list/', apis.FormGroupListApi.as_view(), name='form_group'),
    # path('form-group/', apis.AddToFormGroupCollectionApi.as_view())
]