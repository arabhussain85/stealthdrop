from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Transfer
import uuid
from django.http import FileResponse
from .models import Transfer

@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        
        # Generate UUID and save file
        file_id = uuid.uuid4()
        fs = FileSystemStorage(location='media/')
        filename = fs.save(f"{file_id}-{file.name}", file)
        
        transfer = Transfer.objects.create(
            file_name=file.name,
            file_size=file.size,
            file_id=file_id,
        )
        
        return Response({'file_id': transfer.file_id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def download_file(request, file_id):
    try:
        # Find the transfer object by UUID
        transfer = Transfer.objects.get(file_id=file_id)
        
        # Open the file from the media directory
        file_path = f"media/{transfer.file_id}-{transfer.file_name}"
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=transfer.file_name)
    
    except Transfer.DoesNotExist:
        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
