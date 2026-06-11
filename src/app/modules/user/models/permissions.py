from enum import IntEnum
from app.lib.common import stable_hash

class Permissions(IntEnum):
    USER_ADD = stable_hash('USER_ADD')
    USER_DELETE = stable_hash('USER_DELETE')
    USER_EDIT = stable_hash('USER_EDIT')
    USER_VIEW_LIST = stable_hash('USER_VIEW_LIST')
    USER_VIEW_PROFILE = stable_hash('USER_VIEW_PROFILE')

    ROLE_ADD = stable_hash('ROLE_ADD')
    ROLE_VIEW = stable_hash('ROLE_VIEW')
    ROLE_VIEW_LIST = stable_hash('ROLE_VIEW_LIST')
    ROLE_EDIT = stable_hash('ROLE_EDIT')

    CONTAINER_INFO = stable_hash('CONTAINER_INFO')
    CONTAINER_START = stable_hash('CONTAINER_START')
    CONTAINER_STOP = stable_hash('CONTAINER_STOP')
    CONTAINER_RESTART = stable_hash('CONTAINER_RESTART')
    CONTAINER_DELETE = stable_hash('CONTAINER_DELETE')
    CONTAINER_VIEW_LIST = stable_hash('CONTAINER_VIEW_LIST')
    CONTAINER_EXEC = stable_hash('CONTAINER_EXEC')

    IMAGE_INFO = stable_hash('IMAGE_INFO')
    IMAGE_DELETE = stable_hash('IMAGE_DELETE')
    IMAGE_VIEW_LIST = stable_hash('IMAGE_VIEW_LIST')

    VOLUME_INFO = stable_hash('VOLUME_INFO')
    VOLUME_DELETE = stable_hash('VOLUME_DELETE')
    VOLUME_VIEW_LIST = stable_hash('VOLUME_VIEW_LIST')

    NETWORK_INFO = stable_hash('NETWORK_INFO')
    NETWORK_DELETE = stable_hash('NETWORK_DELETE')
    NETWORK_VIEW_LIST = stable_hash('NETWORK_VIEW_LIST')

    GLOBAL_SETTINGS_VIEW = stable_hash('GLOBAL_SETTINGS_VIEW')
    GLOBAL_SETTINGS_EDIT = stable_hash('GLOBAL_SETTINGS_EDIT')

    @classmethod
    def all(cls):
        """
        Returns all permission values (i.e., stable hashes) as a list.
        """
        return [
            cls.USER_ADD, cls.USER_DELETE, cls.USER_EDIT, cls.USER_VIEW_LIST, cls.USER_VIEW_PROFILE,
            cls.ROLE_ADD, cls.ROLE_VIEW, cls.ROLE_VIEW_LIST, cls.ROLE_EDIT,
            cls.CONTAINER_INFO, cls.CONTAINER_START, cls.CONTAINER_STOP, cls.CONTAINER_RESTART, cls.CONTAINER_DELETE, cls.CONTAINER_VIEW_LIST, cls.CONTAINER_EXEC,
            cls.IMAGE_INFO, cls.IMAGE_DELETE, cls.IMAGE_VIEW_LIST,
            cls.VOLUME_INFO, cls.VOLUME_DELETE, cls.VOLUME_VIEW_LIST,
            cls.NETWORK_INFO, cls.NETWORK_DELETE, cls.NETWORK_VIEW_LIST,
            cls.GLOBAL_SETTINGS_VIEW, cls.GLOBAL_SETTINGS_EDIT
        ]