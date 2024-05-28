from django.urls import path

from . import apis

app_name = 'forms'

urlpatterns = [
    # ============ Forms collection URL's ============ #
    path(
        'form-collection/create/',
        apis.CreateFormCollectionApi.as_view(),
        name='form_collection'
    ),
    path(
        'form-collection/delete/<str:id>/',
        apis.DeleteFormCollectionApi.as_view(),
        name='form_collection_delete'
    ),
    path(
        'form-collection/list/',
        apis.ListFormCollectionApi.as_view(),
        name='form_collection_list'
    ),
    path(
        'form-collection/update/<str:id>/',
        apis.UpdateFormCollectionApi.as_view(),
        name='form_collection_update'
    ),

    # ============ Form group collection URL's ============ #
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
]