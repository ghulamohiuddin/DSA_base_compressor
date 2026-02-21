import os
import zlib
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from .models import CompressedFile
from .huffman import HuffmanCoding


def compress_file(request):
    """
    Main page + compression handler

    Compression types:
    - TXT → Huffman Coding (DSA)
    - Images / PDF / PPT → zlib binary compression

    Levels:
    - fast     → low compression, fast (level 1)
    - balanced → medium (level 6)
    - max      → highest compression (level 9)
    """

    context = {}

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        extension = uploaded_file.name.split('.')[-1].lower()

        # Read compression level from frontend
        level_name = request.POST.get('level', 'balanced')
        
        print(f"[DEBUG] Received level: {level_name}")  # Debug log

        # Map UI → compression level
        LEVEL_MAP = {
            'fast': 1,
            'balanced': 6,
            'max': 9
        }
        level = LEVEL_MAP.get(level_name, 6)
        
        print(f"[DEBUG] Using compression level: {level}")  # Debug log

        # Save original file
        obj = CompressedFile.objects.create(
            original_file=uploaded_file,
            original_size=uploaded_file.size
        )

        # Ensure compressed directory exists
        compressed_dir = os.path.join(settings.MEDIA_ROOT, 'compressed')
        os.makedirs(compressed_dir, exist_ok=True)

        compressed_path = os.path.join(
            compressed_dir,
            f'{obj.id}.bin'
        )

        # ===============================
        # TXT → HUFFMAN (DSA)
        # ===============================
        if extension == 'txt':
            print(f"[DEBUG] Compressing TXT with Huffman, level={level}")
            huffman = HuffmanCoding()
            huffman.compress(
                obj.original_file.path,
                compressed_path,
                level=level
            )

        # ===============================
        # OTHER FILES → ZLIB
        # ===============================
        else:
            print(f"[DEBUG] Compressing {extension.upper()} with zlib, level={level}")
            with open(obj.original_file.path, 'rb') as f:
                data = f.read()

            compressed_data = zlib.compress(data, level=level)

            with open(compressed_path, 'wb') as f:
                f.write(compressed_data)

        # Save compressed info
        obj.compressed_file.name = f'compressed/{obj.id}.bin'
        obj.compressed_size = os.path.getsize(compressed_path)
        obj.save()

        # Calculate space saved
        if obj.original_size > 0:
            space_saved = round(
                (1 - (obj.compressed_size / obj.original_size)) * 100,
                2
            )
        else:
            space_saved = 0.0

        print(f"[DEBUG] Original: {obj.original_size} bytes")
        print(f"[DEBUG] Compressed: {obj.compressed_size} bytes")
        print(f"[DEBUG] Space saved: {space_saved}%")

        context = {
            'original_size': round(obj.original_size / 1024, 2),  # Convert to KB
            'compressed_size': round(obj.compressed_size / 1024, 2),  # Convert to KB
            'space_saved': space_saved,
            'file_id': obj.id,
        }

    return render(request, 'file_compressor/index.html', context)


def download_file(request, file_id):
    """
    Download compressed file
    """
    obj = get_object_or_404(CompressedFile, id=file_id)

    return FileResponse(
        obj.compressed_file.open('rb'),
        as_attachment=True,
        filename=f'compressed_{obj.id}.bin'
    )