import re

from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from pymongo import MongoClient

MONGO_DB = settings.MONGO_DB_NAME

# =============== MongoDB =============== #
def connect_db() -> MongoClient:
    """
    Connecting to MongoDB client.
    """
    db_username = settings.MONGO_USERNAME
    db_pass = settings.MONGO_PASSWORD
    db_host = settings.MONGO_HOST
    db_port = settings.MONGO_PORT

    client = MongoClient(f"mongodb://{db_username}:{db_pass}@{db_host}:{db_port}/")
    return client


def create_form_collection(
        *, name: str, system_name: str, group: str, validator: list,
        meta_data: list, color: str, icon: str
):
    """
    Creating form collection.
    """
    client = connect_db()
    my_db = client[MONGO_DB]
    forms_collection = my_db['forms']

    data = {
        'name': name,
        'system_name': system_name,
        'group': group,
        'validator': validator,
        'meta_data': meta_data,
        'color': color
        # 'icon': icon
        # 'user': user.pk
    }
    forms_collection.insert_one(data)



def create_sys_name_collection():
    """
    Creating collections for each system names.
    """
    pass

def add_to_form_group(*, group: str):
    """
    Append form groups to form_group collection.
    """
    client = connect_db()
    my_db = client[MONGO_DB]
    form_group_collection = my_db['form_group']
    if form_group_collection.find_one() is not None:
        form_group_collection.update_one({}, {'$push': {'groups': group}})
    else:
        form_group_collection.insert_one({'groups': [group]})

def get_form_groups() -> list[str]:
    """
    Return list of groups from form_group collection.
    """
    client = connect_db()
    my_db = client[MONGO_DB]
    form_group_coll = my_db['form_group']
    return form_group_coll.distinct('groups')


# =============== Validators =============== #
def validate_icon_format(icon: str):
    """
    Validating format of the icon.
    """
    supported_format = list(settings.SUPPORTED_ICON_FORMAT)

    if not Path(str(icon).lower()).suffix in supported_format:
        raise ValidationError(
            f"Supported format for icons: {supported_format}",
            code='unsupported_icon_format'
        )

def validate_icon_size(icon: str):
    """
    Validating size of the icon.
    """
    max_size = float(settings.MAX_ICON_SIZE_MB)

    if icon.size > max_size * 1024 * 1024:
        raise ValidationError(
            f"Icon size must be less than {max_size}MB",
            code='icon_size'
        )

def validate_system_name(system_name: str):
    """
    Ensure each system names match with MongoDB naming conventions.
    """
    pattern = r'^[a-z][a-z0-9_]*$'
    if not bool(re.match(pattern, system_name)):
        raise ValidationError(
            'System name must adhere to the specified MongoDB naming conventions.',
            code='mongo_convention_names'
        )
