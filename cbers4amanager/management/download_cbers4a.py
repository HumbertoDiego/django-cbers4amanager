#!/usr/bin/env python3
import os,requests, sys, django
#sys.path.append('/home/capdiego/Documents/cbers4a')  
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download
from process.models import Process, Job, Task
from django.utils import timezone
from django.core.files.base import ContentFile

def get_fname_ext(url):
	direita = url.split("/")[-1]
	esquerda = direita.split("?")[0]
	return esquerda, "".join(esquerda.split(".")[0:-1]), esquerda.split(".")[-1]

def acompanhar(response,download):
	"""
	Função para acompanhamento do andamento do download
	"""
	total_length = response.headers.get('content-length')
	# ERRADO Content-Type	text/html; charset=utf-8
	# CERTO  Content-Type	image/tiff
	if "html" in response.headers.get('content-type'):
		print(response.headers.get('content-type'))
		retorno = b''
	elif total_length is None: # no content length header
		retorno = b''
		download.content_length = 0
		download.save()
	else:
		dl = 0
		total_length = int(total_length)
		download.content_length = total_length
		download.save()
		retorno = b''
		# TODO: Colocar um tempo máximo dentro de cada iteração
		msg_done_anterior = ""
		for data in response.iter_content(chunk_size=4096):
			dl += len(data)
			retorno+=data
			done = int(50 * dl / total_length)
			msg_done = "\r[%s%s]" % ('=' * done, ' ' * (50-done))
			if msg_done!=msg_done_anterior:
				# TODO: Gravar num campo a atualização deste downlaod
				download.progresso = "{:.1f}%".format(dl*100 / total_length)
				download.save()
				msg_done_anterior = msg_done+""
	return retorno

def baixar(download):
	url = download.url
	# Teste OK
	#url = "https://static.djangoproject.com/img/fundraising-heart.cd6bb84ffd33.svg"
	fullfname, fname, ext = get_fname_ext(url)
	download.iniciado_em = timezone.now()
	download.terminado_em = None
	download.progresso = "0.0 %" # dica de que alguem pegou esse download
	download.save()
	try:
		r =requests.get(url,stream=True,timeout=5*60)#5min
		tif = acompanhar(r,download)
	except requests.exceptions.Timeout as e:
		print(str(e))
		try:
			r =requests.get(url,stream=True,timeout=5*60)#5min
			tif = acompanhar(r,download)
		except requests.exceptions.Timeout as e:
			print(str(e))
			r =requests.get(url,timeout=5*60)
			tif = r.content
	except Exception as e:
		print(str(e))
		return 0
	if not tif: return 0
	download.arquivo= ContentFile(tif, name=fullfname)
	download.terminado_em = timezone.now()
	download.finalizado = True
	download.save()
	return 1
	
def main(pks):
	for i in pks:
		try:
			download = Download.objects.get(pk=i)
		except:
			continue
		if download.finalizado: 
			print("%s JÁ FINALIZADO, altere finalizado=False para Repetir."%i)
			continue
		elif download.progresso:
			print("%s JÁ EM ANDAMENTO, altere progresso='' para Repetir."%i)
			continue
		elif not download.url:
			print("%s SEM URL, defina uma url para Repetir."%i)
			continue
		print("INICIADO:",download.nome)
		sucesso = baixar(download)
		if not sucesso:
			download.progresso = None # dica de que dá pra fazer esse download novamente
			download.save()
			print("INTERROMPIDO.")
		else:
			print("ENCERRADO.")

if __name__ == '__main__':
	pks = sys.argv[1:]
	if "--todos" in pks:
		pks = [str(d.pk) for d in Download.objects.all()]
	main(pks)

