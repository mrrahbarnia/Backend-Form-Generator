import pytest

from pymongo import MongoClient
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from ..services import (
    connect_db,
    get_form_groups,
    create_form_collection,
    delete_form_from_form_group,
    get_forms_by_form_groups_name,
    update_form_group_name,
    delete_form_collection,
    list_form_collection,
    update_form_collection

)

pytestmark = pytest.mark.django_db

CREATE_FORM_COLLECTION_UTL = reverse('forms:form_collection')


class TestServices:

    # =============== Forms collection Tests =============== #
    def test_crud_operations_form_collection_services(self) -> None:
        """
        Test creating forms and form_groups successfully.
        """
        sample_user = User.objects.create_user(
            username='sample_user',
            password='sample_password'
        )
        create_form_collection(
            db='test',
            name="Sample",
            system_name="sample",
            group="sample",
            validator=[{'max_length': '25'}, {'min_length': '8'}],
            meta_data=[{'action': 'POST'}],
            color='blue',
            icon=None,
            user=sample_user
        )
        create_form_collection(
            db='test',
            name="Sample2",
            system_name="sample2",
            group="sample1",
            validator=[{'max_length': '25'}, {'min_length': '8'}],
            meta_data=[{'action': 'POST'}],
            color='blue',
            icon=None,
            user=sample_user
        )
        create_form_collection(
            db='test',
            name="Sample3",
            system_name="sample3",
            group="sample1",
            validator=[{'max_length': '25'}, {'min_length': '8'}],
            meta_data=[{'action': 'POST'}],
            color='blue',
            icon=None,
            user=sample_user
        )
        my_db: MongoClient = connect_db(db='test')
        forms_collection = my_db['forms']
        forms_group_collection = my_db['form_groups']
        
        assert len(list_form_collection(db='test')) == 3
        assert forms_collection.count_documents({}) == 3
        assert forms_group_collection.count_documents({}) == 2
        # Test listing all form_groups
        assert len(get_form_groups(db='test')) == 2

        form_obj = forms_collection.find_one({'name': 'Sample2'})
        delete_form_collection(db='test', id=str(form_obj['_id']))

        assert forms_collection.count_documents({}) == 2

        form_obj = forms_collection.find_one({'name': 'Sample'})
        update_form_collection(
            db='test', id=str(form_obj['_id']), updated_info={'name': 'edited'}
        )
        assert forms_collection.find_one({'name': 'edited'}) is not None
        assert forms_collection.find_one({'name': 'Sample'}) is None


        forms_collection.delete_many({})
        forms_group_collection.delete_many({})
    
    # =============== System name collections Tests =============== #
    def test_crud_operations_service_name_collections(self) -> None:
        pass

    


    # =============== Validation Tests =============== #  
    def test_unique_constraint_on_name_field(self) -> None:
        """
        Test checking unique constraint on field name.
        """
        sample_user = User.objects.create_user(
            username='sample_user',
            password='sample_password'
        )
        create_form_collection(
            db='test',
            name="Same_name",
            system_name="sample",
            group="Cars",
            validator=[{'max_length': '25'}, {'min_length': '8'}],
            meta_data=[{'action': 'POST'}],
            color='blue',
            icon=None,
            user=sample_user
        )
        with pytest.raises(APIException):
            create_form_collection(
                db='test',
                name="Same_name",
                system_name="sample2",
                group="Different",
                validator=[{'max_length': '25'}, {'min_length': '8'}],
                meta_data=[{'action': 'POST'}],
                color='blue',
                icon=None,
                user=sample_user
            )
        my_db: MongoClient = connect_db(db='test')
        forms_collection = my_db['forms']
        forms_group_collection = my_db['form_groups']

        assert forms_collection.count_documents({}) == 1
        assert forms_group_collection.count_documents({}) == 1
        forms_collection.delete_many({})
        forms_group_collection.delete_many({})
    
    def test_unique_constraint_on_system_name_field(self) -> None:
        """
        Test checking unique constraint on field system_name.
        """
        sample_user = User.objects.create_user(
            username='sample_user',
            password='sample_password'
        )
        create_form_collection(
            db='test',
            name="sample",
            system_name="same_system_name",
            group="Cars",
            validator=[{'max_length': '25'}, {'min_length': '8'}],
            meta_data=[{'action': 'POST'}],
            color='blue',
            icon=None,
            user=sample_user
        )
        with pytest.raises(APIException):
            create_form_collection(
                db='test',
                name="sample1",
                system_name="same_system_name",
                group="Different",
                validator=[{'max_length': '25'}, {'min_length': '8'}],
                meta_data=[{'action': 'POST'}],
                color='blue',
                icon=None,
                user=sample_user
            )
        my_db: MongoClient = connect_db(db='test')
        forms_collection = my_db['forms']
        forms_group_collection = my_db['form_groups']

        assert forms_collection.count_documents({}) == 1
        assert forms_group_collection.count_documents({}) == 1

        forms_collection.delete_many({})
        forms_group_collection.delete_many({})
    
    def test_system_name_conventional_mongo_names(self, admin_client: APIClient) -> None:
        """
        Test with the system_name which not
        a standard mongoDB convention name.
        """
        wrong_names = [
            '123',
            'Wrong',
            'Wrong example',
            'wrongExample',
            '123exampleAAA123'
        ]
        for name in wrong_names:
            payload = {
                'name': 'sample',
                'system_name': name,
            }
            response: Response = admin_client.post(CREATE_FORM_COLLECTION_UTL, payload, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # =============== Forms groups collection Tests =============== #
    def test_delete_form_groups_and_related_forms(self) -> None:
        """
        Test deleting a specific form group and set the
        group value to empty for related forms.
        """
        my_db: MongoClient = connect_db(db='test')

        forms_collection = my_db['forms']
        forms_group_collection = my_db['form_groups']

        forms_list = [
            {'name': 'Sample_form', 'system_name': 'sample_sys_name', 'group': 'sample'},
            {'name': 'Sample_form2', 'system_name': 'sample_sys_name2', 'group': 'sample'}
        ]
        x = forms_collection.insert_many(forms_list)

        id1, id2 = x.inserted_ids
        forms_group_collection.insert_one({'name': 'sample', 'ids': [id1, id2]})

        assert len(forms_group_collection.find_one({'name': 'sample'})["ids"]) == 2
        assert forms_collection.find_one({'name': 'Sample_form'})['group'] == 'sample'

        delete_form_from_form_group(
            db='test',
            group_name='sample',
            id=id1
        )

        assert len(forms_group_collection.find_one({'name': 'sample'})["ids"]) == 1
        assert forms_collection.find_one({'name': 'Sample_form'})['group'] == ''

        forms_collection.delete_many({})
        forms_group_collection.delete_many({})

    def test_get_forms_with_specific_form_group_name(self) -> None:
        """
        Test get_forms_by_form_groups_name service for
        listing all forms belong to a specific form group.
        """
        my_db: MongoClient = connect_db(db='test')

        forms_collection = my_db['forms']
        forms_group_collection = my_db['form_groups']

        forms_list = [
            {'name': 'Sample_form', 'system_name': 'sample_sys_name', 'group': 'sample'},
            {'name': 'Sample_form2', 'system_name': 'sample_sys_name2', 'group': 'sample'}
        ]
        x = forms_collection.insert_many(forms_list)
        id1, id2 = x.inserted_ids
        forms_group_collection.insert_one({'name': 'sample', 'ids': [id1, id2]})

        with pytest.raises(APIException):
            """
            Give the function not existing form group name.
            """
            get_forms_by_form_groups_name(db='test', group_name='wrong')
        
        # With a existing form group
        assert len(get_forms_by_form_groups_name(db='test', group_name='sample')) == 2

        forms_collection.delete_many({})
        forms_group_collection.delete_many({})
    
    def test_update_form_group_name_and_reflected_in_all_related_forms(
            self
    ) -> None:
        """
        Test update_form_group_name service for updating form group name and
        also after that updating the value of group field for all related forms.
        """
        my_db: MongoClient = connect_db(db='test')

        forms_collection = my_db['forms']
        forms_group_collection = my_db['form_groups']

        forms_list = [
            {'name': 'Sample_form', 'system_name': 'sample_sys_name', 'group': 'sample'},
            {'name': 'Sample_form2', 'system_name': 'sample_sys_name2', 'group': 'sample'}
        ]
        x = forms_collection.insert_many(forms_list)
        id1, id2 = x.inserted_ids
        forms_group_collection.insert_one({'name': 'sample', 'ids': [id1, id2]})

        with pytest.raises(APIException):
            """
            Give the function not existing form group name.
            """
            update_form_group_name(db='test', old_name='wrong', new_name='new')

        assert forms_group_collection.find_one({'name': 'sample'}) is not None
        assert forms_collection.find_one({'group': 'sample'}) is not None
        assert forms_collection.find_one({'group': 'new'}) is None

        update_form_group_name(db='test', old_name='sample', new_name='new')

        assert forms_group_collection.find_one({'name': 'sample'}) is None
        assert forms_collection.find_one({'group': 'new'}) is not None

        forms_collection.delete_many({})
        forms_group_collection.delete_many({})

