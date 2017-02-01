import json
from rest_framework import status
from rest_framework.response import Response


class ErrorResponse(Response):
    """
    API subclass from rest_framework response to simplify constructing error messages
    """
    def __init__(self, form=None, serializer=None, **kwargs):
        super(ErrorResponse, self).__init__(status=status.HTTP_400_BAD_REQUEST)

        data = kwargs
        if not data.get('detail'):
            data['detail'] = "Your request cannot be completed"

        if serializer:
            print serializer.errors
            data['detail'] = serializer.errors.values()[0][0]

        # Build the error part of the message:
        # It should try to use "Code" part of the error as the key for the dict,
        # or Field name
        if form and form.errors.items():
            data['errors'] = {}

            for field, errors in json.loads(form.errors.as_json()).items():
                key = field

                # Since django 1.7 built in validation error also return code
                # Just replace the code from our stamps prefix
                code = errors[0].get('code')
                if code:
                    key = errors[0]['code']

                data['errors'][key] = errors[0]['message']
                message = '%s: %s' % (key, errors[0]['message'])
                data["detail"] = message
                break
        self.data = data
