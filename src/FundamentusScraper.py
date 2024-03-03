import os
import json
import requests
import numpy as np
import pandas as pd
import requests_cache
from io import StringIO
from datetime import datetime
from rich.console import Console


console = Console()


class FundamentusScraper:
    def __init__(self) -> None:
        self.console = Console()

    @staticmethod
    def time() -> str:
        return datetime.now().strftime(format='%H:%M:%S')

    @staticmethod
    def date() -> str:
        return datetime.now().strftime(format='%d-%m-%Y')

    def fundamentus(self, symbols: list) -> pd.DataFrame:
        df_fundamentus = pd.DataFrame()

        hdr = {
            'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
            'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
            'Accept-Encoding': 'gzip, deflate',
        }

        with requests_cache.enabled():
            for symbol in symbols:
                symbol = symbol.upper()
                console.print(f'[[green]Coletando dados fundamentalistas do ativo[/]] :: {symbol}')

                url = f"http://fundamentus.com.br/detalhes.php?papel={symbol}"

                try:
                    content = requests.get(url, headers=hdr)

                    tables_html = pd.read_html(io=StringIO(content.text), decimal=',', thousands='.')
                    df_0 = tables_html[0]
                    df_1 = tables_html[1]
                    df_2 = tables_html[2]
                    df_3 = tables_html[3]

                    df_final = pd.concat(
                        [
                            pd.concat([pd.concat([df_0[0], df_0[2]]), pd.concat([df_0[1], df_0[3]])], axis=1).T,
                            pd.concat([pd.concat([df_1[0], df_1[2]]), pd.concat([df_1[1], df_1[3]])], axis=1).T,
                            pd.concat([pd.concat([df_2[2], df_2[4]]), pd.concat([df_2[3], df_2[5]])], axis=1).T.drop(columns=0),
                            pd.concat([pd.concat([df_3[0], df_3[2]]), pd.concat([df_3[1], df_3[3]])], axis=1).T.drop(columns=0)
                        ], axis=1)


                    df_final.columns = df_final.iloc[0].str.replace(pat='?', repl='')

                    line = df_final[1:]
                    if not line.empty:
                        df_fundamentus = pd.concat([df_fundamentus, line])

                except (ValueError, IndexError): 
                    pass

        columns_to_drop = ['Cart. de Crédito', 'Depósitos', 'Nro. Ações', 'Últ balanço processado', 'Data últ cot']
        columns_to_int = ['Vol $ méd (2m)', 'Valor de mercado', 'Valor da firma', 'Ativo Circulante', 'Dív. Bruta', 'Dív. Líquida', 'Patrim. Líq', 'Patrim Líquido']
        columns_to_float = ['Cotação', 'Min 52 sem', 'Max 52 sem','P/VP', 'FFO/Cota', 'Dividendo/cota', 'VP/Cota', 'P/L', 'P/EBIT', 'PSR', 'LPA', 'Giro Ativos']
        columns_to_format_float = ['FFO Yield', 'Div. Yield', 'Vacância Média', 'Cap Rate', 'Imóveis/PL do FII', 'Cres. Rec (5a)', 'Marg. Bruta', 'Marg. EBIT', 'Marg. Líquida', 'ROIC', 'ROE']
        df_fundamentus = df_fundamentus.replace(r'^-$', '0', regex=True)
        df_fundamentus.fillna(0, inplace=True)

        for to_drop in columns_to_drop:
            try:
                df_fundamentus.drop(columns=[to_drop], inplace=True)
            
            except KeyError:
                pass
        
        for to_int in columns_to_int:
            try:
                df_fundamentus[to_int] = df_fundamentus[to_int].astype(np.int64)

            except KeyError:
                pass

        for to_float in columns_to_float:
            try:
                df_fundamentus[to_float] = df_fundamentus[to_float].astype(float)

            except KeyError:
                pass

        for to_format_float in columns_to_format_float:
            try:
                df_fundamentus[to_format_float] = df_fundamentus[to_format_float].str.replace(pat='.', repl='').str.replace(pat=',', repl='.').str.replace(pat='%', repl='').astype(float)

            except KeyError:
                pass

        df_fundamentus = df_fundamentus.reset_index(drop=True) 

        return df_fundamentus


class Main:
    def __init__(self) -> None:
        try:
            # Abrindo o arquivo json com os dados
            with open(file='config/settings.json', mode='r', encoding='utf-8') as file_obj:
                self.config = json.load(file_obj)
            
            self.scraper = FundamentusScraper()

        except FileNotFoundError:
            console.print(f"[[bold red]Arquivo de configuração não encontrado.[/]]")

    def main(self, save_file=False) -> None:
        symbols = self.config['base_symbols']

        df_fundamentus = self.scraper.fundamentus(symbols=symbols)
        
        if save_file:
            self.save_as_file(df=df_fundamentus)

        else:
            print(df_fundamentus)

    def save_as_file(self, df: pd.DataFrame) -> None:
        # Criando a pasta onde seram salvos os arquivos
        save_folder = self.config['save_folder']
        try:
            os.mkdir(path=save_folder)
        
        except FileExistsError:
            pass
        
        filename = f'{self.config['save_folder']}/Relatório de indicadores fundamentalistas ({self.scraper.date()}).xlsx'
        df.to_excel(filename, index=False)
        console.print(f'[[bold yellow]Arquivo excel gerado com o resultado. ([white]{filename}[/])[/]]')
