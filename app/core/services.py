import re
import gridfs
import uuid
from pprint import pprint

from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.errors import WriteError
from pymongo import MongoClient, GEOSPHERE

MONGO_DB = settings.MONGO_DB_NAME

# =============== MongoDB =============== #
def connect_db(*, db: str) -> MongoClient:
    """
    Connecting to MongoDB client.
    """
    db_username = settings.MONGO_USERNAME
    db_pass = settings.MONGO_PASSWORD
    db_host = settings.MONGO_HOST
    db_port = settings.MONGO_PORT

    if db == 'prod':
        client = MongoClient(f"mongodb://{db_username}:{db_pass}@{db_host}:{db_port}/")
        my_db = client[MONGO_DB]
        return my_db

    if db == 'test':
        client = MongoClient(f"mongodb://{db_username}:{db_pass}@{db_host}:{db_port}/")
        test_db = client['test']
        return test_db

# =============== System name collection services =============== #
def create_sys_name_collection(*, db: str, system_name: str, validators: dict) -> None:
    """
    Creating collections for each system names.
    """
    my_db = connect_db(db=db)
    validation_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "properties": {
                "fields": {
                    "bsonType": "object",
                    "properties": validators
                }
            }
        }
    }
    pprint(validation_schema)
    system_name_collection = my_db.create_collection(system_name, validator=validation_schema)
    system_name_collection.create_index([("the_geom", GEOSPHERE)])

def list_system_name_collections(*, db: str) -> list:
    """
    Listing all name of the system_name collections.
    """
    my_db = connect_db(db=db)
    collection_names = my_db.list_collection_names()
    try:
        collection_names.remove('forms')
        collection_names.remove('form_groups')
        return collection_names
    except ValueError:
        # TODO: Logging if a client wants to list system names collection before creating any.
        pass

def list_documents_from_system_name(*, db: str, user: User, collection_name: str) -> None:
    """
    Listing all documents withing a system name collection.
    Admin user => Return all documents.
    Normal user => Return only documents which created by the authenticated user.
    """
    # TODO: Change the functionality after authorization logic.
    my_db = connect_db(db=db)
    if collection_name in my_db.list_collection_names():
        system_name_collection = my_db[collection_name]
        system_name_documents = list()
        if user.is_staff:
            for document in system_name_collection.find({}):
                system_name_documents.append(document)
        else:
            for document in system_name_collection.find({'user_id': user.pk}):
                system_name_documents.append(document)
        return system_name_documents
    raise NotFound(
        {'message': 'There is no collection with the provided name.'}
    )

def insert_doc_in_sys_name_coll(
        *, db: str, collection_name: str, fields: dict, user_id: int
) -> None:
    my_db = connect_db(db=db)
    print(fields)
    if collection_name in my_db.list_collection_names():
        system_name_collection = my_db[collection_name]
        inserted_data = {'user_id': user_id, 'the_geom': [], **fields}
        pprint(inserted_data)
        try:
            system_name_collection.insert_one(inserted_data)
        except WriteError as e:
            raise ValidationError(
                {'message': f'{e}'}
            )
    else:
        raise NotFound(
            {'message': 'There is no collection with the provided system name.'}
        )

def delete_system_name_document(
        *, db: str, user: User, collection_name: str, id: str
) -> None:
    """
    Deleting a specific system name document with the provided id.
    Admin user can delete every documents but normal user only
    can delete documents which created by his own.
    """
    my_db = connect_db(db=db)
    
    if collection_name in my_db.list_collection_names():
        service_name_collection = my_db[collection_name]
        if user.is_staff:
            try:
                if service_name_collection.find_one({'_id': ObjectId(id)}):
                    service_name_collection.delete_one({'_id': ObjectId(id)})
                else:
                    raise NotFound(
                        {'message': 'There is no document with the provided id.'}
                    )
            except InvalidId:
                raise NotFound(
                    {'message': 'There is no document with the provided id.'}
                )
        else:
            try:
                if service_name_collection.find_one({'_id': ObjectId(id)}):
                    if service_name_collection.find_one({'_id': ObjectId(id), 'user_id': user.pk}):
                        service_name_collection.delete_one({'_id': ObjectId(id)})
                    else:
                        raise PermissionDenied(
                            {"message": "You are not the owner of this document."}
                        )
                else:
                    raise NotFound(
                        {'message': 'There is no document with the provided id.'}
                    )
            except InvalidId:
                raise NotFound(
                    {'message': 'There is no document with the provided id.'}
                )
    else:
        raise NotFound(
            {'message': 'There is no collection with the provided collection name.'}
        )

def update_system_name_document(
        *, db: str, collection_name: str, user: User, id: str, fields: dict
) -> None:
    """
    Update document within system_name collection with the provided
    collection name and document id.Admin users can update every document
    but normal users can only update document which created by his own.
    """
    my_db = connect_db(db=db)

    if collection_name in my_db.list_collection_names():
        service_name_collection = my_db[collection_name]
        if user.is_staff:
            try:
                if service_name_collection.find_one({'_id': ObjectId(id)}):
                    service_name_collection.update_one({'_id': ObjectId(id)}, {'$set': fields})
                else:
                    raise NotFound(
                        {'message': 'There is no document with the provided id.'}
                    )
            except InvalidId:
                raise NotFound(
                    {'message': 'There is no document with the provided id.'}
                )
        else:
            try:
                if service_name_collection.find_one({'_id': ObjectId(id)}):
                    if service_name_collection.find_one({'_id': ObjectId(id), 'user_id': user.pk}):
                        service_name_collection.update_one({'_id': ObjectId(id)}, {'$set': fields})
                    else:
                        raise PermissionDenied(
                            {"message": "You are not the owner of this document."}
                        )
                else:
                    raise NotFound(
                        {'message': 'There is no document with the provided id.'}
                    )
            except InvalidId:
                raise NotFound(
                    {'message': 'There is no document with the provided id.'}
                )
    else:
        raise NotFound(
            {'message': 'There is no collection with the provided collection name.'}
        )

# =============== Forms collection services =============== #
def create_form_collection(
        *, db: str,  name: str, system_name: str, group: str, validator: dict,
        meta_data: dict, color: str, icon: str, user: User
):
    """
    Creating form collection.
    """
    # TODO: Create a storage for storing icons.
    my_db = connect_db(db=db)

    forms_collection = my_db['forms']
    file_id = None
    object_id = ObjectId()

    if icon:
        fs = gridfs.GridFS(my_db)
        file_id = fs.put(icon, filename=str(uuid.uuid4()).split('-')[0])

    if forms_collection.find_one({'name': name}) is not None:
        raise ValidationError(
            {'message': 'Name must be unique.'},
            code='unique_constraint_name'
        )

    if forms_collection.find_one({'system_name': system_name}) is not None:
        raise ValidationError(
            {'message': 'System name must be unique.'},
            code='unique_constraint_system_name'
        )

    create_sys_name_collection(
        db=db, system_name=system_name, validators=validator
    )

    data = {
        'name': name,
        'system_name': system_name,
        'group': group,
        'meta_data': meta_data,
        'color': color,
        'icon': file_id,
        'user_id': user.pk
    }
    object = forms_collection.insert_one(data)
    object_id = object.inserted_id
    add_to_form_group(db=db, group=group, id=object_id)

def delete_form_collection(*, db: str, id: str) -> None:
    """
    Delete forms collection with provided id.
    """
    my_db = connect_db(db=db)
    forms_collection = my_db['forms']
    try:
        form_object = forms_collection.find_one({'_id': ObjectId(id)})
        if form_object:
            forms_collection.delete_one({'_id': ObjectId(id)})
        else:
            raise NotFound(
                {'message': 'There is no form collection with the provided id.'}
            )
    except InvalidId:
        raise NotFound(
            {'message': 'There is no form collection with the provided id.'}
        )

def list_form_collection(*, db: str):
    """
    List forms collection.
    """
    my_db = connect_db(db=db)
    forms_collection = my_db['forms']
    forms_collection_list = list()
    for document in forms_collection.find({}):
        forms_collection_list.append(document)
    return forms_collection_list

def update_form_collection(*, db: str, id: str, updated_info: dict):
    """
    Update an existing forms collection.
    Only the system name field cannot change.
    """
    my_db = connect_db(db=db)
    forms_collection = my_db['forms']
    try:
        form_object = forms_collection.find_one({'_id': ObjectId(id)})
        if form_object:
            if updated_info.get('system_name'):
                raise ValidationError(
                    {'message': 'System name field cannot change.'}
                )
            else:
                forms_collection.update_one({'_id': ObjectId(id)}, {'$set': updated_info})
                return forms_collection.find_one({'_id': ObjectId(id)})
        else:
            raise NotFound(
                {'message': 'There is no form with the provided id.'}
            )
    except InvalidId:
        raise NotFound(
                {'message': 'There is no form with the provided id.'}
            )


# =============== Form groups collection services =============== #
def add_to_form_group(*, db: str, group: str, id: ObjectId):
    """
    Append form groups to form_group collection.
    """
    my_db = connect_db(db=db)
    form_groups_collection = my_db['form_groups']
    if group in form_groups_collection.distinct('name'):
        form_groups_collection.update_one({'name': group}, {'$push': {'ids': id}})
    else:
        ids = list()
        ids.append(id)
        form_groups_collection.insert_one({'name': group, 'ids': ids})

def get_form_groups(*, db: str) -> list[str]:
    """
    Return list of groups from form_group collection.
    """
    my_db = connect_db(db=db)
    form_groups_collection = my_db['form_groups']
    return form_groups_collection.distinct('name')

def get_forms_by_form_groups_name(*, db: str, group_name: str):
    """
    Return a list of forms with a specific form_group name.
    """
    my_db = connect_db(db=db)
    form_groups_collection = my_db['form_groups']
    form_collection = my_db['forms']
    form_group = form_groups_collection.find_one({'name': group_name})
    form_list = list()
    if form_group:
        for i in form_group['ids']:
            form_list.append(form_collection.find_one({'_id': i}))
        return form_list
    else:
        raise NotFound(
            {'message': 'There is no group exist with the provided group_name.'}
        )

def delete_form_from_form_group(*, db: str, group_name: str, id: str):
    """
    Deleting a form with provided id from form
    group with provided group_name.after that automatically
    set group to empty for that document.
    """
    my_db = connect_db(db=db)
    form_groups_collection = my_db['form_groups']
    forms_collection = my_db['forms']
    if group:= form_groups_collection.find_one({'name': group_name}):
        try:
            if ObjectId(id) in group['ids']:
                form_groups_collection.update_one({'name': group_name}, {'$pull': {'ids': ObjectId(id)}})
                forms_collection.update_one({'_id': ObjectId(id)}, {'$set': {'group': ''}})
            else:
                raise NotFound(
                    {'message': 'There is no instance with the provided _id.'}
                )
        except InvalidId:
            raise NotFound(
                {'message': 'There is no instance with the provided _id.'}
            )
    else:
        raise NotFound(
            {'message': 'There is no group with the provided group name.'}
        )

def update_form_group_name(*, db: str, old_name: str, new_name: str):
    """
    Updating a form group name with the provided new name.
    Also updating all forms with the provided old name.
    """
    my_db = connect_db(db=db)
    form_groups_collection = my_db['form_groups']
    forms_collection = my_db['forms']

    if form_groups_collection.find_one({'name': old_name}):
        form_groups_collection.update_one({'name': old_name}, {'$set': {'name': new_name}})
        forms_collection.update_many({'group': old_name}, {'$set': {'group': new_name}})
    else:
        raise NotFound(
            {'message': 'There is no form group with the provided old_name.'}
        )


# =============== Validators =============== #
def validate_icon_format(icon: str):
    """
    Validating format of the icon.
    """
    supported_format = list(settings.SUPPORTED_ICON_FORMAT)

    if not Path(str(icon).lower()).suffix in supported_format:
        raise DjangoValidationError(
            f"Supported format for icons: {supported_format}",
            code='unsupported_icon_format'
        )

def validate_icon_dimensions(icon: str):
    """
    Validating icon by their dimensions.
    """
    max_width = settings.MAX_ICON_WIDTH
    max_height = settings.MAX_ICON_HEIGHT
    width, height = get_image_dimensions(icon)
    if width > max_width or height > max_height:
        raise DjangoValidationError(
            f'Maximum dimensions of icon is {max_width}*{max_height}.',
            code='icon_dimension_exceeded'
        )

def validate_system_name(system_name: str):
    """
    Ensure each system names match with MongoDB naming conventions.
    """
    pattern = r'^[a-z][a-z0-9_]*$'
    if not bool(re.match(pattern, system_name)):
        raise DjangoValidationError(
            'System name must adhere to the specified MongoDB naming conventions.',
            code='mongo_convention_names'
        )
