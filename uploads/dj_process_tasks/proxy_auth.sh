#!/bin/bash
cat << EOF
                  #------------------------------------------------------------------#
                  #                                                                  #
                  #                                                                  #
                  #        A U T E N T I C A Ç Ã O  P R O X Y  4 C T A  !!           #
                  #                                                                  #
                  #                                                                  #
                  #------------------------------------------------------------------#
Pedir atualizações para: humberto-xingu@live.com
uso: ./proxy_auth.sh [cpf] [senha]
teste: ping www.google.com
EOF
cpf=$1
senha=$2
if [[ $cpf = "" ]]
then
read -p "Digite o CPF: " cpf
fi
if [[ $senha = "" ]]
then
read -p "Digite a senha: " senha
fi

P=$(curl -v --silent --stderr - "http://10.78.4.24:1000/logout?" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.5" -H "Accept-Encoding: gzip, deflate" -H "Connection: keep-alive" -H "Upgrade-Insecure-Requests: 1" -H "Pragma: no-cache" -H "Cache-Control: no-cache" | grep "Location" | cut -d " " -f 3)
#The $URL contains a \r (CR) at the end (0d). Remove it with
P=${P%$'\r'}
base=$(echo $P | cut -d '?' -f 1)
direita=$(curl "$P" --silent --stderr - -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.5" -H "Accept-Encoding: gzip, deflate" -H "Referer: http://intranet/" -H "Connection: keep-alive" -H "Upgrade-Insecure-Requests: 1" -H "Pragma: no-cache" -H "Cache-Control: no-cache" )
#### Split by word 
delimiter='magic" value="'
string=$direita$delimiter
myarray=()
while [[ $string ]]; do
  myarray+=( "${string%%"$delimiter"*}" )
  string=${string#*"$delimiter"}
done
direita="${myarray[1]}"
##### Fim Split by word
magic=$(echo $direita | cut -d '"' -f 1)
echo $P
echo $base
echo $magic
url="4Tredir=$P&magic=$magic&username=$cpf&password=$senha"
curl "$base" -X POST -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.5" -H "Accept-Encoding: gzip, deflate" -H "Content-Type: application/x-www-form-urlencoded" -H "Origin: $base" -H "Connection: keep-alive" -H "Referer: $P" -H "Upgrade-Insecure-Requests: 1" -H "Pragma: no-cache" -H "Cache-Control: no-cache" --data-raw $url

#<html><head><title>Firewall Authentication</title></head><body>Redirected to the authentication portal.
#<a href="http://10.78.4.24:1000/portal?0554:1000/portal?055b256a48722086">Click here</a> to load the
# authentication page.</body></html>
