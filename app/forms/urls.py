from django.urls import path

from . import apis

urlpatterns = [
    path('form-collection/', apis.CreateFormCollectionApi.as_view(), name='form_collection'),
    path('form-groups/list/', apis.FormGroupListApi.as_view(), name='form_group'),
    path(
        'form-groups/list/<str:group_name>/',
        apis.RetrieveFormGroupsDocumentApi.as_view(),
        name='list_forms_form_group'
    ),
    path(
        'form-groups/delete/<str:group_name>/<str:id>/',
        apis.DeleteFormGroupsDocumentApi.as_view(),
        name='delete_form_from_form_group'
    ),
    path(
        'form-groups/update/<str:group_name>/',
        apis.UpdateFormGroupApi.as_view(),
        name='update_form_group'
    )
    # path('form-group/', apis.AddToFormGroupCollectionApi.as_view())
]