from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

DICTIONARY_TYPES = [dict, OrderedDict, ReturnDict]
LIST_TYPES = [list, ReturnList]

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Enjoy",
    ),
    public=True,
    permission_classes=(AllowAny,)
)
