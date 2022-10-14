#!/usr/bin/env python3
from email import header
from pySmartDL import SmartDL
import os,requests, sys, django, time
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import GDALRaster

def set_bounds(d):
	rst = GDALRaster(d.arquivo, write=False)
	xmin, ymin, xmax, ymax = rst.extent
	pol = 'POLYGON(({xmin} {ymin},{xmax} {ymin},{xmax} {ymax},{xmin} {ymax},{xmin} {ymin}))'.format(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
	print()
	print(pol)
	poly = GEOSGeometry(pol,srid=rst.srid)
	d.bounds = poly
	d.save()

def baixar(download):
	url = download.url
	# Teste OK
	out = os.path.join(settings.MEDIA_ROOT,'a','bandas',download.nome)
	download.iniciado_em = timezone.now()
	download.arquivo = out
	obj = SmartDL(url,out, progress_bar=False)
	obj.start(blocking=False)
	download.content_length = obj.get_final_filesize()
	while not obj.isFinished():
		# [*] 0.23 Mb / 0.37 Mb @ 88.00Kb/s [60%, 2s left]
		pbar = "%s / %s @ %s [%d%%, %s]"%(obj.get_dl_size(human=True), 
								obj.get_final_filesize(human=True),
								obj.get_speed(human=True),
								obj.get_progress()*100,
								obj.get_eta(human=True)
						)
		download.progresso = obj.get_dl_size()
		download.progress_bar = pbar
		download.save()
		print(pbar)
		time.sleep(1)
	if obj.isSuccessful():
		download.progresso = download.content_length = os.path.getsize(out)
		pbar = "%s / %s"%(obj.get_dl_size(human=True), 
						 obj.get_final_filesize(human=True)
						)
		download.progress_bar = pbar
		download.finalizado = True
		download.terminado_em = timezone.now()
		download.save()
	else:
		print("There were some errors:")
		for e in obj.get_errors():
				print(str(e))
		return 0
	return 1
	
def main(pks):
	for i in pks:
		try:
			download = Download.objects.get(pk=i)
		except:
			continue
		# Os Downloads são tão demorados que esse status pode ter sido alterado
		if download.finalizado: continue
		if not download.url:
			print("%s SEM URL, defina uma url para Repetir."%i)
			continue
		elif download.progresso and download.progresso==download.content_length:
			print("%s JÁ FINALIZADO, altere progresso=0 para Repetir."%i)
			continue
		else:
			try:
				print("%s %s - INICIANDO."%(i,download.nome))
				sucesso = baixar(download)
			except KeyboardInterrupt:
				print('KeyboardInterrupt')
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)
			except Exception as e:
				print("%s"%i,"- PULANDO devido a",e)
				continue
			if not sucesso:
				download.progresso = None
				download.save()
				print(" - INTERROMPIDO.")
				continue
			else:
				set_bounds(download)
				print(" - ENCERRADO.")

if __name__ == '__main__':
	pks = sys.argv[1:]
	if "--todos" in pks:
		pks = [str(d.pk) for d in Download.objects.filter(finalizado=False).order_by('prioridade','id').all()]
	main(pks)
	

