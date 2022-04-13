import os,requests
import PIL
from PIL import Image

def get_list(file):
	f = open(file, mode='r', encoding="utf-8") # aqui o cursor está no início
	text = f.read() # após a leitura o cursor segue para o final
	linhas = [u for u in text.split("\n") if u]
	return linhas

def get_fname_ext(url):
	direita = url.split("/")[-1]
	esquerda = direita.split("?")[0]
	return esquerda, "".join(esquerda.split(".")[0:-1]), esquerda.split(".")[-1]

def acompanhar(response):
	"""
	Função para acompanhamento do andamento do download
	"""
	total_length = response.headers.get('content-length')
	if total_length is None: # no content length header
		retorno = b''
	else:
		dl = 0
		total_length = int(total_length)
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

def download(url):
	fullfname, fname, ext = get_fname_ext(url)
	if ext=="xml": return 0
	if "BAND0" in fname or "BAND4" in fname: return 0
	if not os.path.exists(fullfname):
		print()	
		print("Baixando arquivo:",fullfname)	
		try:
			r =requests.get(links[i],stream=True,timeout=5*60)#5min
			tif = acompanhar(r)
		except requests.exceptions.Timeout as e:
			print(str(e))
			try:
				r =requests.get(links[i],stream=True,timeout=5*60)#5min
				tif = acompanhar(r)
			except requests.exceptions.Timeout as e:
				print(str(e))
				r =requests.get(links[i])
				tif = r.content
		except Exception as e:
			print(str(e))
			return 0
		with open(fullfname, "wb") as f:
			f.seek(0,2)
			f.tell()
			f.write(tif)
	else:
		print("Arquivo já gravado:",fname+"."+ext)

def thumb(infile):
	name, ext = "".join(infile.split(".")[0:-1]), infile.split(".")[-1]
	if ext=="tif":
		outfile = name + ".jpeg"
		if os.path.exists(outfile):
			print("WARNING:",infile,"já existe.")
			return 0
		try:
			im = Image.open(infile).convert('RGB')
		except PIL.Image.DecompressionBombError:
			print("WARNING:",infile,PIL.Image.DecompressionBombError)
			return 0
		print("Gerando thumbnail:",infile, im.mode)
		im.thumbnail((200,200))
		im.save(outfile, "JPEG", quality=70)

def norm(band):
    band_min, band_max = band.min(), band.max()
    return ((band - band_min)/(band_max - band_min))

links_file = "inpe_catalog_2022_4_8_9_30_35.txt"
links = get_list(links_file)

for i in range(len(links)):
	download(links[i])

"""
gdal_merge.py -separate -o rgb.tif CBERS_4A_WPM_20220330_230_108_L4_BAND3.tif CBERS_4A_WPM_20220330_230_108_L4_BAND2.tif CBERS_4A_WPM_20220330_230_108_L4_BAND1.tif 
gdal_pansharpen.py CBERS_4A_WPM_20220330_230_108_L4_BAND0.tif CBERS_4A_WPM_20220330_230_108_L4_BAND3.tif CBERS_4A_WPM_20220330_230_108_L4_BAND2.tif CBERS_4A_WPM_20220330_230_108_L4_BAND1.tif pansharpened.tif
gdal_pansharpen.py NB-20-Z-C-V-4-NE_pan.tif NB-20-Z-C-V-4-NE_rgb.tif NB-20-Z-C-V-4-NE_pansharpened.tif

"""