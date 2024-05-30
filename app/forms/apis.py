from django.conf import settings
from rest_framework import serializers, status, permissions
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

from drf_spectacular.utils import extend_schema

from core.services import (
    validate_icon_format,
    validate_icon_dimensions,
    get_form_groups,
    create_form_collection,
    get_forms_by_form_groups_name,
    delete_form_from_form_group,
    validate_system_name,
    update_form_group_name,
    list_form_collection,
    delete_form_collection,
    update_form_collection,
    list_system_name_collections,
    list_documents_from_system_name,
    insert_doc_in_sys_name_coll,
    delete_system_name_document,
    update_system_name_document
)
from .pagination import (
    get_paginated_response_context,
    LimitOffsetPagination
)

# ============ Forms collection API's ============ #
class CreateFormCollectionApi(APIView):
    permission_classes = [permissions.IsAdminUser]

    class CreateFormCollectionInputSerializer(serializers.Serializer):
        name = serializers.CharField()
        system_name = serializers.CharField(validators=(validate_system_name, ))
        group = serializers.CharField(required=False)
        validator = serializers.DictField(child=serializers.JSONField(), required=False)
        meta_data = serializers.DictField(child=serializers.JSONField(), required=False)
        color = serializers.CharField(required=False)
        icon = serializers.FileField(validators=(
            validate_icon_format,
            validate_icon_dimensions,
        ), required=False)
        user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    @extend_schema(request=CreateFormCollectionInputSerializer)
    def post(self, request: Request, *args, **kwargs) -> Response:
        input_serializer = self.CreateFormCollectionInputSerializer(
            data=request.data, context={'request': request}
        )
        input_serializer.is_valid(raise_exception=True)
        create_form_collection(
            db='prod',
            name=input_serializer.validated_data.get('name'),
            system_name=input_serializer.validated_data.get('system_name'),
            group=input_serializer.validated_data.get('group'),
            validator=input_serializer.validated_data.get('validator'),
            meta_data=input_serializer.validated_data.get('meta_data'),
            color=input_serializer.validated_data.get('color'),
            icon=input_serializer.validated_data.get('icon'),
            user=input_serializer.validated_data.get('user')
        )

        return Response(
            {'message': 'Form created successfully'},
            status=status.HTTP_201_CREATED
        )


class DeleteFormCollectionApi(APIView):
    """
    Delete a form collection with provided id only by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request: Request, id: str = None, *args, **kwargs) -> Response:
        delete_form_collection(db='prod', id=id)

        return Response(
            {'message': 'The form collection deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class ListFormCollectionApi(APIView):
    """
    List forms collection.
    """
    permission_classes = [permissions.IsAdminUser]

    class Pagination(LimitOffsetPagination):
        default_limit = int(settings.PAGINATION_DEFAULT_LIMIT)

    class OutputListFormCollectionSerializer(serializers.Serializer):
        _id = serializers.CharField()
        name = serializers.CharField()
        system_name = serializers.CharField()
        group = serializers.CharField()
        meta_data = serializers.DictField()
        color = serializers.CharField()
        icon = serializers.FileField()

    @extend_schema(responses=OutputListFormCollectionSerializer)
    def get(self, request: Request, *args, **kwargs) -> Response:
        forms = list_form_collection(db='prod')
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputListFormCollectionSerializer,
            queryset=forms,
            request=request,
            view=self
        )


class UpdateFormCollectionApi(APIView):
    """
    Update an existing forms collection only by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    class UpdateFormCollectionSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        group = serializers.CharField(required=False)
        # validator = serializers.DictField(required=False)
        meta_data = serializers.DictField(required=False)
        color = serializers.CharField(required=False)
        icon = serializers.FileField(required=False)

    @extend_schema(
            request=UpdateFormCollectionSerializer
    )
    def put(
            self, request: Request, id: str | None = None, *args, **kwargs
    ) -> Response:
        input_serializer = self.UpdateFormCollectionSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        update_form_collection(
            db='prod',
            id=id,
            updated_info=input_serializer.validated_data
        )

        return Response(
            {'message': 'The form collection updated successfully'},
            status=status.HTTP_200_OK
        )


# ============ System name collection API's ============ #
class ListSystemNameCollectionApi(APIView):
    """
    Listing all system_name collections.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, *args, **kwargs) -> Response:
        collection_names = list_system_name_collections(db='prod')

        return Response(collection_names, status=status.HTTP_200_OK)


class InsertSystemNameDocumentApi(APIView):
    """
    Creating a document within a system_name based
    on url parameter system_name collection.
    """
    permission_classes = [permissions.IsAuthenticated]

    class CreateSystemNameCollectionSerializer(serializers.Serializer):
        fields = serializers.DictField(child=serializers.JSONField())

    @extend_schema(
            request=CreateSystemNameCollectionSerializer
    )
    def post(
            self, request: Request, collection_name: str | None = None, *args, **kwargs
    ) -> Response:
        input_serializer = self.CreateSystemNameCollectionSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        insert_doc_in_sys_name_coll(
            db='prod',
            collection_name=collection_name,
            user_id=request.user.pk,
            fields=input_serializer.validated_data
        )

        return Response(
            {'message': 'Document inserted successfully'},
            status=status.HTTP_201_CREATED
        )


class ListDocumentsFromSystemNameApi(APIView):
    """
    Listing all documents within a specific system name collection.
    """
    permission_classes = [permissions.IsAuthenticated]

    class Pagination(LimitOffsetPagination):
        default_limit = int(settings.PAGINATION_DEFAULT_LIMIT)

    class OutputListDocumentSerializer(serializers.Serializer):
        _id = serializers.CharField()
        user_id = serializers.CharField()
        fields = serializers.DictField()

    @extend_schema(
            responses=OutputListDocumentSerializer
    )
    def get(
            self, request: Request, collection_name: str | None = None, *args, **kwargs
    ) -> Response:
        documents = list_documents_from_system_name(
            db='prod', user=request.user, collection_name=collection_name
        )
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputListDocumentSerializer,
            queryset=documents,
            request=request,
            view=self
        )


class DeleteSystemNameDocumentApi(APIView):
    """
    Delete documents within a specific system collection.
    Admin user can delete every documents but normal user can only
    delete the documents which created by his own.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(
            self, request: Request, collection_name: str, id: str, *args, **kwargs
    ) -> Response:
        delete_system_name_document(
            db='prod',
            user=request.user,
            collection_name=collection_name,
            id=id
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateSystemNameDocumentApi(APIView):
    """
    Update documents within a specific system collection.
    Admin user can update every documents but normal user can only
    update the documents which created by his own.
    """
    permission_classes = [permissions.IsAuthenticated]

    class UpdateSystemNameDocumentSerializer(serializers.Serializer):
        fields = serializers.DictField(child=serializers.JSONField())
    
    @extend_schema(request=UpdateSystemNameDocumentSerializer)
    def put(
        self, request: Request, collection_name: str, id: str, *args, **kwargs
    ) -> Response:
        input_serializer = self.UpdateSystemNameDocumentSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        update_system_name_document(
            db='prod',
            collection_name=collection_name,
            user=request.user,
            id=id,
            fields=input_serializer.validated_data
        )

        return Response(
            {'message': 'Document updated successfully.'},
            status=status.HTTP_200_OK
        )

# ============ Form group collection API's ============ #
class DeleteFormGroupsDocumentApi(APIView):
    """
    Delete a specific form from a form_group only by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def delete(
            self, request: Request, group_name: str | None = None,
            id: int | None = None,  *args, **kwargs
    ) -> Response:
        delete_form_from_form_group(
            db='prod',
            group_name=group_name,
            id=id
        )
        return Response(
            {'message': 'Group deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class RetrieveFormGroupsDocumentApi(APIView):
    """
    List all forms belong to a specific form_groups
    collection which given by the url parameter.
    """
    permission_classes = [permissions.IsAdminUser]

    class OutputRetrieveFormGroupsSerializer(serializers.Serializer):
        _id = serializers.CharField()
        name = serializers.CharField()
        system_name = serializers.CharField()
    
    @extend_schema(responses=OutputRetrieveFormGroupsSerializer)
    def get(
        self, request: Request, group_name: str | None = None, *args, **kwargs
    ) -> Response:
        forms = get_forms_by_form_groups_name(
            db='prod', group_name=group_name
        )
        output_serializer = self.OutputRetrieveFormGroupsSerializer(forms, many=True).data
        return Response(output_serializer, status=status.HTTP_200_OK)


class UpdateFormGroupApi(APIView):
    """
    Updating form_groups name and group field for
    all forms belong to that only by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    class InputUpdateFormGroupSerializer(serializers.Serializer):
        new_name = serializers.CharField()

    @extend_schema(request=InputUpdateFormGroupSerializer)
    def post(self, request: Request, group_name: str, *args, **kwargs) -> Response:
        input_serializer = self.InputUpdateFormGroupSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        update_form_group_name(
            db='prod',
            old_name=group_name,
            new_name=input_serializer.validated_data.get('new_name')
        )

        return Response(
            {'message': 'Group name updated in form_groups collection and all forms belong to this group.'},
            status=status.HTTP_200_OK
        )


class FormGroupListApi(APIView):
    """
    listing all form groups with unauthenticated users.
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        try:
            groups_list = get_form_groups(db='prod')

            return Response(groups_list, status=status.HTTP_200_OK)
        except Exception as ex:
            return APIException({'message': f'ex'})
