import os,requests, sys, django
#sys.path.append('/home/capdiego/Documents/cbers4a')  
sys.path.append(os.getcwd()) 

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cbers4a.settings")
django.setup()

from cbers4amanager.models import Download
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
	if total_length is None: # no content length header
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
				print(msg_done, end="", flush=True)
				msg_done_anterior = msg_done+""
	return retorno

def baixar(download):
	url = download.url
	# Teste OK
	url = "https://static.djangoproject.com/img/fundraising-heart.cd6bb84ffd33.svg"
	fullfname, fname, ext = get_fname_ext(url)
	download.iniciado_em = timezone.now()
	download.save()
	try:
		r =requests.get(url,stream=True,)
		tif = acompanhar(r,download)
	except:
		r =requests.get(url)
		tif = r.content
	download.arquivo= ContentFile(tif, name=fullfname)
	download.terminado_em = timezone.now()
	download.finalizado = True
	download.save()
	

def main(pks):
	for i in pks:
		try:
			download = Download.objects.get(pk=i)
		except:
			continue
		if download.finalizado: continue
		print("INICIADO:",download.nome)
		baixar(download)
		print("TERMINADO:",download.nome)

if __name__ == '__main__':
	pks = sys.argv[1:]
	main(pks)

