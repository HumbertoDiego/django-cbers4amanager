#!/usr/bin/env python3
import sys
def main(lat:float=0,lon:float=0):
    """
    Entrada: lat, lon
    Saída:  Indice de Nomenclatura (INOM) utilizado pelo 
            Sistema Cartográfico Nacional (SCN) Brasileiro
    """
    #lat, lon = 5.3283,-60.1725 #NB-20-Z-B-VI-2-SO
    #lat, lon = 5.1917,-60.1929 #NB-20-Z-B-VI-4-NO 
    #lat, lon = -5.001,-70.001#SB-19-V-D-I-2-NE
    #lat, lon = -4.998,-70.003#SB-19-V-B-IV-4-SE 
    #lat, lon = -4.998,-69.998#SB-19-V-B-V-3-SO
    #lat, lon = -5.001,-69.998#SB-19-V-D-II-1-NO
    #lat, lon = -5,-70######## ?????? = SB-19-V-D-I-2-NE  ????????

    hemisferio= 'N' if lat>=0 else 'S'
    fuso = ''
    alfa = ''
    vy_xz = ''
    vx_yx = ''
    vxyz = ''
    ab_cd = ''
    ac_bd = ''
    abcd = ''
    iiv_iiv_iiivi = ''
    iiiiii_ivvvi = ''
    iiiiiiivvvi = ''
    umtres_doisquatro = ''
    umdois_tresquatro = ''
    umdoistresquatro = ''
    none_sose = ''
    noso_nese = ''
    nonesose = ''
    #fuso: (Lim esq, Lim dir),
    fusos={
        '18': (-78,-72)
    }
    f0_esq = -180
    dx=6 
    for i in range(1,26):
        fusos[str(i)]=(f0_esq,f0_esq+dx)
        if f0_esq<lon <=f0_esq+dx:
            fuso = str(i)
            dx=3
            if f0_esq<lon <=f0_esq+dx:
                vy_xz = 'VY'
            else:
                vy_xz = 'XZ'
                f0_esq+=dx
            dx=1.5
            if f0_esq<lon <=f0_esq+dx:
                ac_bd = 'AC'
            else:
                ac_bd = 'BD'
                f0_esq+=dx
            dx=0.5
            if f0_esq<lon<=f0_esq+dx:
                iiv_iiv_iiivi = 'I_IV'
            elif f0_esq+dx<lon<=f0_esq+dx+dx:
                iiv_iiv_iiivi = 'II_V'
                f0_esq+=dx
            else:
                iiv_iiv_iiivi = 'III_VI'
                f0_esq=f0_esq+dx+dx
            dx=0.25
            if f0_esq<lon<=f0_esq+dx:
                umtres_doisquatro = '13'
            else:
                umtres_doisquatro = '24'
                f0_esq+=dx
            dx=0.125
            if f0_esq<lon<=f0_esq+dx:
                noso_nese = 'NO_SO'
            else:
                noso_nese = 'NE_SE'
                f0_esq+=dx
            break
        f0_esq+=dx

    #fuso_lat: (Lim inf, Lim sup),
    fusos_lat = {
        'A':(0,4)
    }
    e0 = 0
    sinal = -1 if hemisferio=='S' else 1
    dy=4
    for c in "ABCDEFGHIFKLMNOPQRSTUV":
        fusos_lat[c]=(e0,e0+sinal*dy)
        if min(e0, e0+sinal*dy)<lat<=max(e0, e0+sinal*dy):
            alfa = c
            dy=2
            if min(e0, e0+sinal*dy)<lat<=max(e0, e0+sinal*dy):
                vx_yx = 'VX' if sinal<0 else 'YZ'
            else:
                vx_yx = 'YZ' if sinal<0 else 'VX'
                e0 = e0 + sinal*dy
            dy=1
            if min(e0, e0+sinal*dy)<lat<=max(e0, e0+sinal*dy):
                ab_cd = 'AB' if sinal<0 else 'CD'
            else:
                ab_cd = 'CD' if sinal<0 else 'AB'
                e0 = e0 + sinal*dy
            dy=0.5
            if min(e0, e0+sinal*dy) < lat <= max(e0, e0+sinal*dy):
                iiiiii_ivvvi = 'I_II_III' if sinal<0 else 'IV_V_VI'
            else:
                iiiiii_ivvvi = 'IV_V_VI' if sinal<0 else 'I_II_III'
                e0 = e0 + sinal*dy
            dy=0.25
            if min(e0, e0+sinal*dy) < lat <=max(e0, e0+sinal*dy):
                umdois_tresquatro = '12' if sinal<0 else '34'
            else:
                umdois_tresquatro = '34' if sinal<0 else '12'
                e0 = e0 + sinal*dy
            dy=0.125
            if min(e0, e0+sinal*dy) < lat <=max(e0, e0+sinal*dy):
                none_sose = 'NO_NE' if sinal<0 else 'SO_SE'
            else:
                none_sose = 'SO_SE' if sinal<0 else 'NO_NE'
                e0 = e0 + sinal*dy
            break
        e0 = e0 + sinal*dy

    inom1m = hemisferio+alfa+"-"+fuso
    vxyz = ''.join(set(vy_xz).intersection(vx_yx))
    inom500k = inom1m+"-"+vxyz
    abcd = ''.join(set(ac_bd).intersection(ab_cd))
    inom250k = inom500k+"-"+abcd
    iiiiiiivvvi = ''.join(set(iiv_iiv_iiivi.split("_")).intersection(iiiiii_ivvvi.split("_")))
    inom100k = inom250k + iiiiiiivvvi
    umdoistresquatro = ''.join(set(umtres_doisquatro).intersection(umdois_tresquatro))
    inom50k = inom100k + umdoistresquatro
    nonesose = ''.join(set(noso_nese.split("_")).intersection(none_sose.split("_")))
    inom25k  = inom50k + nonesose
    print(hemisferio+alfa+"-"+fuso+"-"+vxyz+"-"+abcd+"-"+iiiiiiivvvi+"-"+umdoistresquatro+"-"+nonesose)
    return inom25k,inom50k,inom100k,inom250k,inom500k,inom1m

if __name__ == '__main__':
    try:
        main(float(sys.argv[1]),float(sys.argv[2]))
    except Exception as e:
        print(str(e))
        print("Uso:")
        print("\tpython3 latlon2inom.py 5.3283 -60.1725")
        print("\t",end="")
        main(5.3283, -60.1725 )