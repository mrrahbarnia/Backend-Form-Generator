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
    update_form_group_name
)


class CreateFormCollectionApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
            group_name=group_name
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
            groups_list = get_form_groups()

            return Response(groups_list, status=status.HTTP_200_OK)
        except Exception as ex:
            return APIException({'message': f'ex'})
