from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache

class QuotaUploadHandler(FileUploadHandler):
    # This handler limits the size of uploaded files to a certain quota
    def __init__(self, request):
        super().__init__(request)
        # Get the user's quota from the cache or database
        self.user_quota = cache.get(f"{request.user.id}_quota", 100)
        # Initialize the amount of data received
        self.amount_received = 0

    def receive_data_chunk(self, raw_data, start):
        # Update the amount of data received
        self.amount_received += len(raw_data)
        # Check if the quota is exceeded
        if self.amount_received > self.user_quota:
            # Raise an exception to stop the upload
            raise Exception(f"Your upload quota is {self.user_quota} bytes")
        # Return the data as is
        return raw_data

    def file_complete(self, file_size):
        # This method is called when a file is fully uploaded
        # You can perform any actions here, such as logging, updating database, etc.
        # For example, you can reduce the user's quota by the file size
        self.user_quota -= file_size
        cache.set(f"{self.request.user.id}_quota", self.user_quota)
