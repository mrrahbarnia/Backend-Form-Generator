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
    validate_system_name
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

        return Response('OK')


class FormGroupListApi(APIView):
    """
    listing all form groups.
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        try:
            groups_list = get_form_groups()

            return Response(groups_list, status=status.HTTP_200_OK)
        except Exception as ex:
            return APIException({'message': f'ex'})
