from rest_framework import status
from rest_framework.response import Response


class ErrorResponse(Response):
    """
    API subclass from rest_framework response to simplify constructing error messages
    """
    def __init__(self, form=None, **kwargs):
        super(ErrorResponse, self).__init__(status=status.HTTP_400_BAD_REQUEST)

        data = kwargs
        if not data.get('error_description'):
            data['error_description'] = "Your request cannot be completed"

        if form is not None and form.errors:
            error_description = '%s: %s' % (form.errors.items()[0][0], form.errors.values()[0][0])
            data['error_description'] = error_description

        self.data = data
