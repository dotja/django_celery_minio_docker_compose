from celery import shared_task
from .models import EditPhoto
from django.conf import settings
from django.contrib.auth import get_user_model
from sketchify import sketch
import os
from .helpers import MediaBucketMapper


@shared_task
def convert_to_sketch(user_id, photo_name):
	user_model = get_user_model()
	curr_user = user_model.objects.get(user_id=user_id)
	user_photos = EditPhoto.objects.get(app_user=curr_user, photo=photo_name)
	name_w_ext = user_photos.photo.name
	name_wo_ext = os.path.splitext(name_w_ext)[0]
	##
	media_bucket_client = MediaBucketMapper(
		endpoint_url=settings.AWS_S3_ENDPOINT_URL,
		aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
		aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
	)
	media_bucket_client.download_file_to_tmp(settings.AWS_STORAGE_BUCKET_NAME, name_w_ext)
	local_path = f'/tmp/{name_w_ext}'
	sketch.normalsketch(
		local_path,
		'/tmp/',
		name_wo_ext
	)
	media_bucket_client.upload_file_from_tmp(settings.AWS_STORAGE_BUCKET_NAME, f'{name_wo_ext}.png')
	user_photos.photo.name = f'{name_wo_ext}.png'
	user_photos.edited = True
	user_photos.save()
	return
