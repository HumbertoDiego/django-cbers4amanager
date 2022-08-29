#!/usr/bin/env python3
from email import header
import os,requests, sys, django, time
#sys.path.append('/home/capdiego/Documents/cbers4a')  
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download
from django.utils import timezone
from django.core.files.base import ContentFile

headers = {
	'Host': 'www2.dgi.inpe.br',
	'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0',
	'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
	'Upgrade-Insecure-Requests': '1'
}

def print_history(r):
	if r.history:
		print("Request was redirected")
		for resp in r.history:
			print(resp.status_code, resp.url)
		print("Final destination:")
		print(r.status_code, r.url)
	else:
		print("Request was not redirected")

def get_fname_ext(url):
	direita = url.split("/")[-1]
	esquerda = direita.split("?")[0]
	return esquerda, "".join(esquerda.split(".")[0:-1]), esquerda.split(".")[-1]

def resume_download(fileurl, resume_byte_position):
	resume_header = {'Range': 'bytes=%d-' % resume_byte_position}
	resume_header.update(headers)
	#print(resume_header)
	return requests.get(fileurl, verify=False, headers=resume_header, stream=True, allow_redirects=True,timeout=60)

def baixar(download):
	url = download.url
	# Teste OK
	#url = "https://static.djangoproject.com/img/fundraising-heart.cd6bb84ffd33.svg"
	fullfname, fname, ext = get_fname_ext(url)
	out = os.path.join(settings.MEDIA_ROOT,'bandas',download.nome)
	current_downloaded = 0 
	download.iniciado_em = timezone.now()
	download.terminado_em = None
	download.arquivo = out
	download.save()
	if os.path.exists(out):
		a_or_w = "ab"
		exist_size = os.path.getsize(out)
	else:
		a_or_w = "wb"
		exist_size = 0
	try:
		if download.progresso and download.progresso==exist_size:
			print("Continuando download do byte",exist_size)
		elif download.progresso and download.progresso!=exist_size:
			print("Continuando download confiar no arquivo local em vez de progresso",exist_size)
		r = resume_download(url, exist_size)
		print(r.request.headers)
		print(r.headers)
		requested_length = r.headers.get('content-length')
		if "html" in r.headers.get('content-type'):
			print(r.headers.get('content-type'),r.content)
			if r.status_code == 416: # Requested Range Not Satisfiable
				download.content_length = exist_size
				download.progresso = exist_size
				download.finalizado = True
				download.terminado_em = timezone.now()
		elif requested_length is None: 
			print("no content length header")
			download.content_length = 0
			download.save()
		else:
			requested_length = int(requested_length)
			if exist_size==0:
				# 1ª Rodada deste download
				download.content_length = requested_length
				total_length = requested_length+0
				download.save()
			else:
				total_length = download.content_length
			ini = time.time()
			speed = 0.001
			with open(out,a_or_w) as f:
				for data in r.iter_content(chunk_size=4096):
					f.write(data)
					exist_size += len(data)
					current_downloaded += len(data)
					download.progresso = exist_size
					delta_t = time.time() - ini
					if delta_t!=0:
						speed =  current_downloaded/1000/delta_t
					download.save()
					print("\r{:.1f}% - {:.1f} KB/s".format(exist_size*100/total_length,speed), end="")
			download.finalizado = True
			download.terminado_em = timezone.now()
	except requests.exceptions.Timeout as e:
		print(str(e))
		return 0
	except Exception as e:
		print(str(e))
		return 0
	download.save()
	return 1
	
def main(pks):
	for i in pks:
		try:
			download = Download.objects.get(pk=i)
		except:
			continue
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
				print('Interrupted')
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
				print(" - ENCERRADO.")

if __name__ == '__main__':
	pks = sys.argv[1:]
	if "--todos" in pks:
		pks = [str(d.pk) for d in Download.objects.filter(finalizado=False).order_by('id').all()]
	main(pks)
	

