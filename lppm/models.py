from django.db import models
from django.contrib.auth.models import User
# from django.core.validators import FileExtensionValidator
from django.dispatch import receiver
import os


def upload_penelitian(instance, filename):
	return '/'.join(['penelitian', instance.dosen.user.username, filename])


def upload_pengabdian(instance, filename):
	return '/'.join(['pengabdian', instance.dosen.user.username, filename])


def upload_location(instance, filename):
	return '/'.join(['foto', instance.dosen.user.username, filename])


class Fakultas(models.Model):
	nama = models.CharField(max_length=30)
	dekan = models.CharField(max_length=60)

	def __str__(self):
		return self.nama


class Prodi(models.Model):
	fakultas = models.ForeignKey(Fakultas, on_delete=models.CASCADE)
	nama = models.CharField(max_length=30)
	ketua = models.CharField(max_length=60)
	jenjang = models.CharField(max_length=5)

	def __str__(self):
		return self.nama


class Dosen(models.Model):
	prodi = models.ForeignKey(Prodi, on_delete=models.CASCADE)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	alamat = models.TextField()
	tlp = models.CharField(max_length=25)
	foto = models.ImageField(
		upload_to=upload_location,
		default='default.jpg',
		)

	def __str__(self):
		return self.user.first_name


class Penelitian(models.Model):
	dosen = models.ForeignKey(Dosen, on_delete=models.CASCADE)
	file = models.FileField( # file must .pdf/.word
		upload_to=upload_penelitian,
		blank=False,
		null=False,
		# validators=[FileExtensionValidator(['pdf'])],
	)
	status = models.BooleanField(default=False) # False = Not Accepted, True = Accepted
	# validasi_dsn = models.CharField(max_length=120, blank=True)
	# timestamp_validasi = models.DateTimeField()
	tahun = models.CharField(max_length=5, blank=False)
	judul = models.CharField(max_length=120, blank=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	lokasi = models.CharField(max_length=120, blank=False)


class Pengabdian(models.Model):
	dosen = models.ForeignKey(Dosen, on_delete=models.CASCADE)
	file = models.FileField( # file must .pdf/.word
		upload_to=upload_penelitian,
		blank=False,
		null=False,
		# validators=[FileExtensionValidator(['pdf'])],
	)
	status = models.BooleanField(default=False) # False = Not Accepted, True = Accepted
	# validasi_dsn = models.CharField(max_length=120, blank=True)
	# timestamp_validasi = models.DateTimeField()
	tahun = models.CharField(max_length=5, blank=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	lokasi = models.CharField(max_length=120, blank=False)
	judul = models.CharField(max_length=120, blank=False)


# class Validasi(models.Model):



@receiver(models.signals.post_delete, sender=Penelitian)
def auto_delete_file_on_delete(sender, instance, **kwargs):
	if instance.file:
		if os.path.isfile(instance.file.path):
			os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Penelitian)
def auto_delete_file_on_change(sender, instance, **kwargs):
	if not instance.pk:
		return False
	try:
		old_file = sender.objects.get(pk=instance.pk).file
	except sender.DoesNotExist:
		return False
	new_file = instance.file 
	if not old_file == new_file:
		if os.path.isfile(old_file.path):
			os.remove(old_file.path)


@receiver(models.signals.post_delete, sender=Pengabdian)
def auto_delete_file_on_delete(sender, instance, **kwargs):
	if instance.file:
		if os.path.isfile(instance.file.path):
			os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Pengabdian)
def auto_delete_file_on_change(sender, instance, **kwargs):
	if not instance.pk:
		return False
	try:
		old_file = sender.objects.get(pk=instance.pk).file
	except sender.DoesNotExist:
		return False
	new_file = instance.file 
	if not old_file == new_file:
		if os.path.isfile(old_file.path):
			os.remove(old_file.path)