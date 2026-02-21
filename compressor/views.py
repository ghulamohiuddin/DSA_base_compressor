import os
from django.conf import settings
from django.shortcuts import render, redirect
from .models import CompressedFile
from .huffman import HuffmanCoding

def compress_file(request):
    if request.method == 'POST':
        file = request.FILES['file']

        obj = CompressedFile.objects.create(
            original_file=file,
            original_size=file.size
        )

        huffman = HuffmanCoding()
        compressed_path = os.path.join(
            settings.MEDIA_ROOT, 'compressed', f'{obj.id}.bin'
        )

        codes = huffman.compress(obj.original_file.path, compressed_path)

        obj.compressed_file.name = f'compressed/{obj.id}.bin'
        obj.compressed_size = os.path.getsize(compressed_path)
        obj.save()

        request.session['codes'] = codes
        request.session['file_id'] = obj.id

        return redirect('success')

    return render(request, 'compress.html')


def decompress_file(request):
    file_id = request.session['file_id']
    obj = CompressedFile.objects.get(id=file_id)

    huffman = HuffmanCoding()
    output_path = os.path.join(
        settings.MEDIA_ROOT, 'decompressed', f'{obj.id}.txt'
    )

    huffman.decompress(
        obj.compressed_file.path,
        output_path,
        request.session['codes']
    )

    obj.decompressed_file.name = f'decompressed/{obj.id}.txt'
    obj.save()

    return redirect('success')


def success(request):
    return render(request, 'success.html')
