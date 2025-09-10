import requests
from django.core.exceptions import PermissionDenied


class CustomSession(requests.Session):
    def __init__(self, request=None, *args, **kwargs):
        """
        Initializes a new instance of the class.

        Parameters:
            request (optional): The request object. Defaults to None.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.request_obj = request

    def custom_request(self, *args, **kwargs):
        """
        Sends a custom request and returns the response.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            response: The response object.

        Raises:
            PermissionDenied: If the response status code is 503 (Service Unavailable).
        """
        response = super().request(*args, **kwargs)

        # Check if the response status code is 503
        if response.status_code == 503:
            raise PermissionDenied("503 Service Unavailable")

        return response
