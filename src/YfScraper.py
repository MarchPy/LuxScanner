import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from rich.console import Console


console = Console()


class YfScraper:
    def __init__(self, symbol: str, start_date: int, end_date: int, interval: str) -> None:
        self.symbol = symbol
        self.interval = interval
        self.start_date_timestamp, self.end_date_timestamp = self.convert_data_to_timestamp(
            start_date=start_date,
            end_date=end_date
        )

    def collect_data(self) -> pd.DataFrame:
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }

        url = f"https://query1.finance.yahoo.com/v7/finance/download/{self.symbol}.SA?period1={self.start_date_timestamp}&period2={self.end_date_timestamp}&interval={self.interval}"
        content = requests.get(url=url, headers=hdr).text
        df = pd.read_csv(filepath_or_buffer=StringIO(initial_value=content))
        if not df.empty:
            console.print(f"[[bold green]Histórico de preços coletados para o símbolo[/]]")
            return df
        
        else:
            if df.columns.to_list()[0] == '404 Not Found: Timestamp data missing.':
                console.print(f"[[bold red]Dados não encontrados no período definido para o símbolo[/]]")
            elif df.columns.to_list()[0] == '404 Not Found: No data found':
                console.print(f"[[bold red]Dados não encontrados para o símbolo[/]]")

            return df
    
    def time(self):
        return datetime.now().strftime(format='%H:%M:%S')

    def convert_data_to_timestamp(self, start_date, end_date) -> tuple:
        start_data_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_data_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        return start_data_timestamp, end_data_timestamp

