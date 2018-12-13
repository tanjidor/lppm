from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import View
from django.http import JsonResponse
from .models import Fakultas, Prodi, Dosen, Penelitian, Pengabdian
import datetime
from .forms import PenelitianForm, PengabdianForm
# from django.db.models.signals import post_save, pre_save
from notifications.signals import notify
# from django.contrib.auth import get_user_model



# def notifPenelitianCreate(sender, instance, **kwargs):
# 	# user = []
# 	# user.append(User.objects.get(username='admin'))
# 	# user = User.objects.all()
# 	#user = User.objects.get(username='dosen1')
# 	# print(instance.pk)
# 	# print(sender)
# 	# notif = user.notifications.get(actor=instance)
# 	# print(notif.pk)
# 	# for key, value in kwargs.items():
# 	# 	user = User.objects.get(pk=value)
# 	user = User.objects.get(pk=instance.dosen.user.pk)
# 	#try:
# 		# cek_penelitian = get_object_or_404(Penelitian, pk=instance.pk)
# 		# print(cek_penelitian)
# 		# Penelitian.objects.get(pk=instance.pk)
# 	#if cek_penelitian:
# 	notify.send(instance, recipient=user, verb="mengupdate Penelitian {}.".format(instance.judul))
# 	#else:
# 	#except:
# 	#notify.send(instance, recipient=user, verb="menambahkan Penelitian baru.")
# # post_save.connect(notifPenelitianCreate, sender=Penelitian)
# #pre_save.connect(notifPenelitianCreate, sender=Penelitian)


# def notifPengabdian(sender, instance, created, **kwargs):
# 	# user = []
# 	# user.append(User.objects.get(username='admin'))
# 	# user = User.objects.all()
# 	user = User.objects.get(username='dosen1')
# 	notify.send(instance, recipient=user, verb="menambahkan Pengabdian baru.")
# post_save.connect(notifPengabdian, sender=Pengabdian)


def notifPenelitianUpdate(user, pk_penerima):
	penerima = User.objects.get(pk=pk_penerima)
	notify.send(user, recipient=penerima, verb="Update Penelitan.")



def awal(request):
	awal = True
	return render(request, 'awal.html', {'awal': awal})


def penelitian_statistik(request):
	try:
		user = get_object_or_404(User, pk=request.user.pk)
	except:
		user = ""
	statistik_penelitian = True
	fakultas = Fakultas.objects.all()
	penelitian = {}
	for i in fakultas:
		penelitian[i.nama] = {}
		prodi = Prodi.objects.filter(fakultas=i)
		for j in prodi:
			penelitian[i.nama][j.nama] = len(Penelitian.objects.filter(dosen__prodi=j).exclude(status=False))
	context = {
		'user': user,
		'statistik_penelitian': statistik_penelitian,
		'penelitian': penelitian,
	}
	return render(request, 'penelitian_statistik.html', context)


class PenelitianChart(APIView):
	authentication_classes = []
	permission_classes = []
	
	def get(self, request, format=None):
		labels = []
		default_items = []
		tahun = str(datetime.datetime.now().year)
		for i in range(14):
			labels.append(int(tahun) - i)
		for i in labels:
			default_items.append(len(Penelitian.objects.filter(tahun=str(i)).exclude(status=False)))
		labels.reverse() # list tahun
		default_items.reverse() # list penelitian
		data = {
			"labels": labels,
			"default": default_items,
		}
		return Response(data)


def pengabdian_statistik(request):
	try:
		user = get_object_or_404(User, pk=request.user.pk)
	except:
		user = ""
	statistik_pengabdian = True
	fakultas = Fakultas.objects.all()
	pengabdian = {}
	for i in fakultas:
		pengabdian[i.nama] = {}
		prodi = Prodi.objects.filter(fakultas=i)
		for j in prodi:
			pengabdian[i.nama][j.nama] = len(Pengabdian.objects.filter(dosen__prodi=j).exclude(status=False))
	context = {
		'user': user,
		'statistik_pengabdian': statistik_pengabdian,
		'pengabdian': pengabdian,
	}
	return render(request, 'pengabdian_statistik.html', context)


class PengabdianChart(APIView):
	authentication_classes = []
	permission_classes = []
	
	def get(self, request, format=None):
		labels = []
		default_items = []
		tahun = str(datetime.datetime.now().year)
		for i in range(14):
			labels.append(int(tahun) - i)
		for i in labels:
			default_items.append(len(Pengabdian.objects.filter(tahun=str(i)).exclude(status=False)))
		labels.reverse() # list tahun
		default_items.reverse() # list penelitian
		data = {
			"labels": labels,
			"default": default_items,
		}
		return Response(data)


@login_required
def home(request):
	beranda = True
	user = User.objects.get(pk=request.user.pk)
	context = {
		'user': user,
		'beranda': beranda,
	}
	return render(request, 'home.html', context)


@login_required
def penelitian_list_self(request):
	user = User.objects.get(pk=request.user.pk)
	list_penelitian_self = Penelitian.objects.filter(dosen=user.dosen.pk).order_by('-id')
	penelitian_list_self = True
	query = request.GET.get('q')
	if query:
		list_penelitian_self = list_penelitian_self.filter(
			Q(judul__icontains=query) |
			Q(tahun=query)
		).distinct()
	paginator = Paginator(list_penelitian_self, 10) # Show 25 contacts per page
	page = request.GET.get('page')
	list_penelitian_self1 = paginator.get_page(page)
	formPenelitian = PenelitianForm(request.POST or None, request.FILES or None)
	if request.method == 'POST':
		aksi = request.POST.get('aksi')
		if aksi == "update_penelitian":
			pk_penelitian = request.POST.get('pk_penelitian')
			penelitian_instance = get_object_or_404(Penelitian, pk=pk_penelitian)
			formPenelitian = PenelitianForm(request.POST or None, request.FILES or None, instance=penelitian_instance)
			simpan = formPenelitian.save(commit=False)
			simpan.save()
			# penelitian_instance.judul = request.POST.get('judul')
			# penelitian_instance.tahun = request.POST.get('tahun')
			# penelitian_instance.lokasi = request.POST.get('lokasi')
			# penelitian_instance.file = request.FILES['file']
			# penelitian_instance.save()
			# fak = {'ea': user.pk}
			# post_save.connect(notifPenelitianCreate, sender=Penelitian)
			#notifPenelitianCreate(sender=Penelitian, instance=simpan.pk)
			# ============================================================================================
			# dosen_list = Dosen.objects.all()
			# for i in dosen_list:
			# 	notifPenelitianUpdate(user, i.user.pk)
			penerima = User.objects.get(username='dosen1')
			notify.send(simpan, recipient=penerima, verb="Updated Penelitan.")
			messages.success(request, "Edit Penelitian Sukses !!!")
			return redirect('lppm:penelitian_list_self')
		elif aksi == "delete_penelitian":
			pk_penelitian = request.POST.get('pk_penelitian')
			penelitian_instance = get_object_or_404(Penelitian, pk=pk_penelitian)
			penelitian_instance.delete()
			messages.success(request, "Hapus Penelitian Sukses !!!")
			return redirect('lppm:penelitian_list_self')
		else:
			if formPenelitian.is_valid():
				simpan = formPenelitian.save(commit=False)
				simpan.dosen = Dosen.objects.get(pk=user.dosen.pk)
				simpan.save()
				# post_save.connect(notifPenelitianCreate, sender=Penelitian)
				penerima = User.objects.get(username='dosen1')
				notify.send(simpan, recipient=penerima, verb="Created Penelitan.")
				messages.success(request, "Penelitian Berhasil Dibuat !!!")
				return redirect('lppm:penelitian_list_self')
	context = {
		'penelitian_list_self': penelitian_list_self,
		'formPenelitian': formPenelitian,
		'user': user,
		'list_penelitian_self1': list_penelitian_self1,
	}
	return render(request, 'penelitian_self.html', context)


@login_required
def pengabdian_list_self(request):
	user = User.objects.get(pk=request.user.pk)
	list_pengabdian_self = Pengabdian.objects.filter(dosen=user.dosen.pk).order_by('-id')
	pengabdian_list_self = True
	query = request.GET.get('q')
	if query:
		list_pengabdian_self = list_pengabdian_self.filter(
			Q(judul__icontains=query) |
			Q(tahun=query)
		).distinct()
	paginator = Paginator(list_pengabdian_self, 5) # Show 25 contacts per page
	page = request.GET.get('page')
	list_pengabdian_self1 = paginator.get_page(page)
	formPengabdian = PengabdianForm(request.POST or None, request.FILES or None)
	if request.method == 'POST':
		aksi = request.POST.get('aksi')
		if aksi == "update_pengabdian":
			pk_pengabdian = request.POST.get('pk_pengabdian')
			pengabdian_instance = get_object_or_404(Pengabdian, pk=pk_pengabdian)
			formPengabdian = PengabdianForm(request.POST or None, request.FILES or None, instance=pengabdian_instance)
			simpan = formPengabdian.save(commit=False)
			simpan.save()
			penerima = User.objects.get(username='dosen1')
			notify.send(simpan, recipient=penerima, verb="Updated Pengabdian.")
			messages.success(request, "Edit Pengabdian Sukses !!!")
			return redirect('lppm:pengabdian_list_self')
		elif aksi == "delete_pengabdian":
			pk_pengabdian = request.POST.get('pk_pengabdian')
			pengabdian_instance = get_object_or_404(Pengabdian, pk=pk_pengabdian)
			pengabdian_instance.delete()
			messages.success(request, "Hapus Pengabdian Sukses !!!")
			return redirect('lppm:pengabdian_list_self')
		else:
			if formPengabdian.is_valid():
				simpan = formPengabdian.save(commit=False)
				simpan.dosen = Dosen.objects.get(pk=request.user.dosen.pk)
				simpan.save()
				penerima = User.objects.get(username='dosen1')
				notify.send(simpan, recipient=penerima, verb="Created Pengabdian.")
				messages.success(request, "Pengabdian Berhasil Dibuat !!!")
				return redirect('lppm:pengabdian_list_self')
	context = {
		'pengabdian_list_self': pengabdian_list_self,
		'formPengabdian': formPengabdian,
		'list_pengabdian_self1': list_pengabdian_self1,
		'user': user,
	}
	return render(request, 'pengabdian_self.html', context)


def penelitian_list(request, nama=None):
	prodi = get_object_or_404(Prodi, nama=nama)
	penelitian_list = Penelitian.objects.filter(dosen__prodi=prodi, status=True)
	query = request.GET.get('q')
	if query:
		penelitian_list = penelitian_list.filter(
			Q(judul__icontains=query) |
			Q(tahun=query)
		).distinct()
	paginator = Paginator(penelitian_list, 10) # Show 25 contacts per page
	page = request.GET.get('page')
	penelitian_list1 = paginator.get_page(page)
	context = {
		'prodi': prodi,
		'penelitian_list1': penelitian_list1,
	}
	return render(request, 'penelitian_list.html', context)


def pengabdian_list(request, nama=None):
	prodi = get_object_or_404(Prodi, nama=nama)
	pengabdian_list = Pengabdian.objects.filter(dosen__prodi=prodi, status=True)
	query = request.GET.get('q')
	if query:
		pengabdian_list = pengabdian_list.filter(
			Q(judul__icontains=query) |
			Q(tahun=query)
		).distinct()
	paginator = Paginator(pengabdian_list, 10) # Show 25 contacts per page
	page = request.GET.get('page')
	pengabdian_list1 = paginator.get_page(page)
	context = {
		'prodi': prodi,
		'pengabdian_list1': pengabdian_list1,
	}
	return render(request, 'pengabdian_list.html', context)


@login_required
def validasi(request, pk=None):
	user = User.objects.get(pk=request.user.pk)
	notif_instance = user.notifications.get(pk=pk)
	notif_instance.mark_as_read()
	validasi = True
	if str(notif_instance.actor_content_type) == "penelitian":
		validasi_tipe = "Penelitian"
		validasi_instance = get_object_or_404(Penelitian, pk=notif_instance.actor.pk)
	else:
		validasi_tipe = "Pengabdian"
		validasi_instance = get_object_or_404(Pengabdian, pk=notif_instance.actor.pk)
	if request.method == "POST":
		action = request.POST.get('validation')
		if action == "good":
			validasi_instance.status = True
			validasi_instance.save()
			notify.send(validasi_instance, recipient=validasi_instance.dosen.user, verb="{1} {2} valid".format(validasi_tipe, validasi_instance.judul))
			messages.success(request, "File {} valid !!!".format(validasi_tipe))
		elif action == "bad":
			validasi_instance.status = False
			validasi_instance.save()
			notify.send(validasi_instance, recipient=validasi_instance.dosen.user, verb="{1} {2} tidak valid".format(validasi_tipe, validasi_instance.judul))
			messages.success(request, "File {} tidak valid !!!".format(validasi_tipe))
		else:
			validasi_instance.status = False
			validasi_instance.save()
			notify.send(validasi_instance, recipient=validasi_instance.dosen.user, verb="{1} {2} dikembalikan".format(validasi_tipe, validasi_instance.judul))
			messages.success(request, "Validasi file {} dibatalkan !!!".format(validasi_tipe))
		return redirect("lppm:validasi", pk=notif_instance.pk)
	context = {
		'user': user,
		'notif_instance': notif_instance,
		'validasi_instance': validasi_instance,
		'validasi_tipe': validasi_tipe,
	}
	return render(request, 'notif.html', context)