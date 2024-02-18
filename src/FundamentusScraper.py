import os
import json
import requests
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
                url = f"http://fundamentus.com.br/detalhes.php?papel={symbol}"

                try:
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

                    self.console.print(f'[[bold white]{self.time()}[/]] -> [[bold green]Dados coletados para o ativo[/]] :: {symbol}')

                except (ValueError, KeyError, PermissionError): 
                    pass
        
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
