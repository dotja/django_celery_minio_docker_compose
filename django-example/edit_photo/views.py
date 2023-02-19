from django.shortcuts import render
from django.contrib import messages
from .models import EditPhoto
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from .tasks import convert_to_sketch
from .helpers import MediaBucketMapper


@login_required(login_url='login')
def edit_photo(request):
	if request.method == 'POST' and request.FILES['photo']:
		photo = request.FILES['photo']
		new_photo = EditPhoto(app_user=request.user, photo=photo)
		new_photo.save()
		res = convert_to_sketch.delay(request.user.user_id, new_photo.photo.name)
		messages.info(request, 'Your image has been submitted to the queue.')
	return render(request, 'edit_photo/edit_photo.html')

@login_required(login_url='login')
def my_photos(request):
	user_photos = EditPhoto.objects.filter(app_user=request.user).exclude(edited=False)
	return render(request, 'edit_photo/my_photos.html', {'photos': user_photos})


@login_required(login_url='login')
def download(request, id):
	user_photos = EditPhoto.objects.filter(app_user=request.user)
	media_bucket_client = MediaBucketMapper(
		endpoint_url=settings.AWS_S3_ENDPOINT_URL,
		aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
		aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
	)
	for p in user_photos:
		if p.id == id:
			media_bucket_client.download_file_to_tmp(settings.AWS_STORAGE_BUCKET_NAME, p.photo.name)
			with open(f'/tmp/{p.photo.name}', 'rb') as imgb:
				response = HttpResponse(imgb.read(), content_type='image/png')
				response['Content-Disposition'] = f'attachment;filename={p.photo.name}'
				return response
	return HttpResponse()
