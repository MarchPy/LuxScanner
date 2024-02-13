import requests
import pandas as pd
import requests_cache
from io import StringIO
from datetime import datetime
from rich.console import Console


console = Console()


tickers = [
  'AALR3','ABCB4','ABEV3','ADHM3','AERI3','AESB3','AFLT3','AGRO3','AGXY3','AHEB3','AHEB5','AHEB6','ALLD3','ALOS3','ALPA3','ALPA4','ALPK3','ALSC3','ALUP11','ALUP3','ALUP4','AMAR3','AMBP3','AMER3','ANDG3B','ANDG4B','ANIM3','APER3','APTI3','APTI4','ARML3','ARZZ3','ASAI3','ATMP3','ATOM3','AURA33','AURE3','AVLL3','AZEV3','AZEV4','AZUL4','B3SA3','BAHI3','BALM3','BALM4','BAUH4','BAZA3','BBAS3','BBDC3','BBDC4','BBML3','BBSE3','BDLL3','BDLL4','BEEF11','BEEF3','BEES3','BEES4','BFRE11','BFRE12','BGIP3','BGIP4','BHIA3','BIDI11','BIDI3','BIDI4','BIOM3','BLAU3','BLUT3','BLUT4','BMEB3','BMEB4','BMGB4','BMIN3','BMIN4','BMKS3','BMOB3','BNBR3','BOAS3','BOBR3','BOBR4','BPAC11','BPAC3','BPAC5','BPAN4','BPAR3','BPAT33','BPHA3','BRAP3','BRAP4','BRBI11','BRBI3','BRBI4','BRFS3','BRGE11','BRGE12','BRGE3','BRGE5','BRGE6','BRGE7','BRGE8','BRIN3','BRIT3','BRIV3','BRIV4','BRKM3','BRKM5','BRKM6','BRML3','BRPR3','BRQB3','BRSR3','BRSR5','BRSR6','BSEV3','BSLI3','BSLI4','BTTL4','CALI3','CALI4','CAMB3','CAMB4','CAML3','CASH3','CASN3','CASN4','CATA3','CATA4','CBAV3','CBEE3','CCRO3','CCXC3','CEAB3','CEBR3','CEBR5','CEBR6','CEDO3','CEDO4','CEEB3','CEEB5','CEEB6','CEED3','CEED4','CEGR3','CEPE3','CEPE5','CEPE6','CESP3','CESP5','CESP6','CGAS3','CGAS5','CGRA3','CGRA4','CIEL3','CLSA3','CLSC3','CLSC4','CMIG3','CMIG4','CMIN3','CMSA3','CMSA4','CNSY3','COCE3','COCE5','COCE6','COGN3','CORR3','CORR4','CPFE3','CPLE11','CPLE3','CPLE5','CPLE6','CPRE3','CREM3','CRFB3','CRIV3','CRIV4','CRPG3','CRPG5','CRPG6','CSAB3','CSAB4','CSAN3','CSED3','CSMG3','CSNA3','CSRN3','CSRN5','CSRN6','CSUD3','CTCA3','CTKA3','CTKA4','CTNM3','CTNM4','CTSA3','CTSA4','CTSA8','CURY3','CVCB3','CXSE3','CYRE3','DASA3','DESK3','DEXP3','DEXP4','DIRR3','DMMO11','DMMO3','DMVF3','DOHL3','DOHL4','DOTZ3','DTCY3','DTCY4','DXCO3','EALT3','EALT4','ECOR3','ECPR3','ECPR4','EEEL3','EEEL4','EGIE3','EKTR3','EKTR4','ELEK3','ELEK4','ELET3','ELET5','ELET6','ELMD3','ELPL3','EMAE3','EMAE4','EMBR3','ENAT3','ENBR3','ENEV3','ENGI11','ENGI3','ENGI4','ENJU3','ENMA3B','ENMA6B','ENMT3','ENMT4','EPAR3','EQPA3','EQPA5','EQPA6','EQPA7','EQTL3','ESPA3','ESTR3','ESTR4','ETER3','EUCA3','EUCA4','EVEN3','EZTC3','FBMC3','FBMC4','FESA3','FESA4','FHER3','FIBR3','FIEI3','FIGE3','FIGE4','FIQE3','FLEX3','FLRY3','FNCN3','FRAS3','FRIO3','FRTA3','FTRT3B','G2DI33','GBIO33','GEPA3','GEPA4','GETT11','GETT3','GETT4','GFSA3','GGBR3','GGBR4','GGPS3','GMAT3','GNDI3','GOAU3','GOAU4','GOLL4','GPAR3','GPIV33','GRAO3','GRND3','GSHP3','GUAR3','GUAR4','HAGA3','HAGA4','HAPV3','HBOR3','HBRE3','HBSA3','HBTS5','HETA3','HETA4','HGTX3','HOOT3','HOOT4','HYPE3','IDVL3','IDVL4','IFCM3','IGBR3','IGSN3','IGTA3','IGTI11','IGTI3','IGTI4','INEP3','INEP4','INNT3','INTB3','IRBR3','ITEC3','ITSA3','ITSA4','ITUB3','ITUB4','JALL3','JBSS3','JFEN3','JHSF3','JOPA3','JOPA4','JSLG3','KEPL3','KLBN11','KLBN3','KLBN4','KRSA3','LAME3','LAME4','LAND3','LAVV3','LCAM3','LEVE3','LHER3','LHER4','LIGT3','LINX3','LIPR3','LJQQ3','LOGG3','LOGN3','LPSB3','LREN3','LTEL3B','LUPA3','LUXM3','LUXM4','LVTC3','LWSA3','MAGG3','MAPT3','MAPT4','MATD3','MBLY3','MDIA3','MDNE3','MEAL3','MELK3','MERC3','MERC4','MGEL3','MGEL4','MGLU3','MILS3','MLAS3','MMAQ3','MMAQ4','MMXM3','MNDL3','MNPR3','MOAR3','MODL11','MODL3','MODL4','MOSI3','MOVI3','MPLU3','MRFG3','MRSA3B','MRSA5B','MRSA6B','MRVE3','MSPA3','MSPA4','MSRO3','MTIG3','MTIG4','MTRE3','MTSA3','MTSA4','MULT3','MWET3','MWET4','MYPK3','NAFG3','NAFG4','NEMO3','NEMO5','NEMO6','NEOE3','NEXP3','NGRD3','NINJ3','NORD3','NRTQ3','NTCO3','NUTR3','ODER4','ODPV3','OFSA3','OGXP3','OIBR3','OIBR4','OMGE3','ONCO3','OPCT3','ORVR3','OSXB3','PARD3','PATI3','PATI4','PCAR3','PCAR4','PDGR3','PDTC3','PEAB3','PEAB4','PETR3','PETR4','PETZ3','PFRM3','PGMN3','PINE3','PINE4','PLAS3','PLPL3','PMAM3','PNVL3','PNVL4','POMO3','POMO4','PORT3','POSI3','POWE3','PPAR3','PPLA11','PRIO3','PRNR3','PSSA3','PTBL3','PTCA11','PTCA3','PTNT3','PTNT4','QGEP3','QUAL3','QUSW3','QVQP3B','RADL3','RAIL3','RAIZ4','RANI3','RANI4','RAPT3','RAPT4','RCSL3','RCSL4','RDNI3','RDOR3','RECV3','REDE3','RENT3','RLOG3','RNEW11','RNEW3','RNEW4','ROMI3','RPAD3','RPAD5','RPAD6','RPMG3','RRRP3','RSID3','RSUL3','RSUL4','SANB11','SANB3','SANB4','SAPR11','SAPR3','SAPR4','SBFG3','SBSP3','SCAR3','SEDU3','SEER3','SEQL3','SGPS3','SHOW3','SHUL3','SHUL4','SIMH3','SLCE3','SLED3','SLED4','SMFT3','SMLS3','SMTO3','SNSY3','SNSY5','SNSY6','SOJA3','SOMA3','SOND3','SOND5','SOND6','SPRI3','SPRI5','SPRI6','SPRT3B','SQIA3','SRNA3','STBP3','STKF3','STTR3','SULA11','SULA3','SULA4','SUZB3','SYNE3','TAEE11','TAEE3','TAEE4','TASA3','TASA4','TCNO3','TCNO4','TCSA3','TECN3','TEKA3','TEKA4','TELB3','TELB4','TEND3','TESA3','TFCO4','TGMA3','TIET11','TIET3','TIET4','TIMS3','TKNO3','TKNO4','TOTS3','TOYB3','TOYB4','TPIS3','TRAD3','TRIS3','TRPL3','TRPL4','TRPN3','TTEN3','TUPY3','TXRX3','TXRX4','UCAS3','UGPA3','UNIP3','UNIP5','UNIP6','USIM3','USIM5','USIM6','VALE3','VAMO3','VBBR3','VITT3','VIVA3','VIVR3','VIVT3','VIVT4','VLID3','VSPT3','VSPT4','VSTE3','VULC3','VVAR11','VVAR4','VVEO3','WEGE3','WEST3','WHRL3','WHRL4','WIZC3','WLMM3','WLMM4','YDUQ3','ZAMP3'
]


def time():
    return datetime.now().strftime(format='%H:%M:%S')


def date():
    return datetime.now().strftime(format='%d-%m-%Y')


def fundamentus(tickers: list):
    df_fundamentus = pd.DataFrame()

    hdr = {
        'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
        'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
        'Accept-Encoding': 'gzip, deflate',
    }

    for ticker in tickers:
        url = f"http://fundamentus.com.br/detalhes.php?papel={ticker}"

        try:
            with requests_cache.enabled():
                content = requests.get(url, headers=hdr)

            tables_html = pd.read_html(io=StringIO(content.text), decimal=',', thousands='.')
            df_0 = tables_html[0]
            df_0 = pd.concat([pd.concat([df_0[0], df_0[2]]), pd.concat([df_0[1], df_0[3]])], axis=1).T
            df_1 = tables_html[1]
            df_1 = pd.concat([pd.concat([df_1[0], df_1[2]]), pd.concat([df_1[1], df_1[3]])], axis=1).T
            df_2 = tables_html[2]
            df_2 = pd.concat([pd.concat([df_2[2], df_2[4]]), pd.concat([df_2[3], df_2[5]])], axis=1).T.drop(columns=0)
            df_3 = tables_html[3]
            df_3 = pd.concat([pd.concat([df_3[0], df_3[2]]), pd.concat([df_3[1], df_3[3]])], axis=1).T.drop(columns=0)
            df = pd.concat([df_0, df_1, df_2, df_3], axis=1)
            df.columns = df.iloc[0].str.replace(pat='?', repl='')

            line = df[1:]
            if not line.empty:
                df_fundamentus = pd.concat([df_fundamentus, line])

            console.print(f'[[bold white]{time()}[/]] -> [[bold green]Dados coletados para o ativo[/]] :: {ticker}')

        except (ValueError, KeyError, PermissionError): None

    df_fundamentus.reset_index(drop=True, inplace=True)
    df_fundamentus = df_fundamentus.replace(r'^-$', '0', regex=True)

    df_fundamentus['Vol $ méd (2m)'] = df_fundamentus['Vol $ méd (2m)'].astype(int)
    df_fundamentus['P/EBIT'] = df_fundamentus['P/EBIT'].astype(float)
    df_fundamentus['P/L'] = df_fundamentus['P/L'].astype(float)
    df_fundamentus['LPA'] = df_fundamentus['LPA'].astype(float)

    columns_to_fmt = [
        'Div. Yield', 'Cres. Rec (5a)', 'Marg. Bruta', 'Marg. EBIT',
        'Marg. Líquida', 'EBIT / Ativo', 'ROIC', 'ROE'
    ]

    for column in columns_to_fmt:
        df_fundamentus[column] = df_fundamentus[column].astype(str)
        df_fundamentus[column] = df_fundamentus[column].str.replace('%', '')
        df_fundamentus[column] = df_fundamentus[column].str.replace('.', '')
        df_fundamentus[column] = df_fundamentus[column].str.replace(',', '.')
        df_fundamentus[column] = df_fundamentus[column].astype(float)

    return df_fundamentus


def main():
    df_fundamentus = fundamentus(tickers=tickers)
    df_fundamentus.to_excel(f'Relatório de indicadores fundamentalistas ({date()}).xlsx')


main()
