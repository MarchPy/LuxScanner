import os
import json
import numpy as np
import pandas as pd
from rich.console import Console
from src.YfScraper import YfScraper
from datetime import datetime, timedelta


console = Console()


class LuxScanner:
    def __init__(self) -> None:
        try:
            with open(file='config/settings.json', mode='r', encoding='utf-8') as file_obj:
                self.__settings = json.load(file_obj)
        except FileNotFoundError:
            console.print(f"[[bold red]Arquivo de configuração não encontrado.[/]]")

    def time(self) -> str:
        return datetime.now().strftime(format='%H:%M:%S')

    def date(self) -> str:
        return datetime.now().strftime(format='%d-%m-%Y')

    def collect_data_from_json_file(self, save_file=False) -> None:
        data = []
        for sector in self.__settings['sectors']:
            sector_name = sector['name']
            status_collect = sector['status']
            symbols = sector['symbols']
            if status_collect == "True":
                for symbol in symbols:
                    console.print(f"[[bold blue]{self.time()}[/]] -> [Setor: [bold yellow]{sector_name}[/]]-[[italic white]Coletando dados do ativo[/]] :: {symbol} -> ", end='')
                    df_yf = self.collect_data_for_symbol(symbol)
                    if not df_yf.empty:
                        close = round(df_yf['Close'].iloc[-1], 2)
                        pc = self.percentage_of_variation(dataframe=df_yf)
                        rsi = self.calculate_rsi(df=df_yf)
                        crossover, volume, check_volume = self.calculate_crossover(df=df_yf)
                        cycle = self.calculate_cycle(df=df_yf)
                        data.append([symbol, close, pc, sector_name, crossover, cycle, volume, check_volume, rsi])

        df_final = self.create_final_dataframe(data)
        self.display_results(df_final, save_file)

    def collect_data_for_symbol(self, symbol) -> pd.DataFrame:
        year_days = 365
        month_days = 30
        period = self.__settings['timeframe']['period']['type']
        if period == "y":
            period = year_days * self.__settings['timeframe']['period']['value']
        elif period == "m":
            period = month_days * self.__settings['timeframe']['period']['value']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        end_date = end_date.strftime(format='%Y-%m-%d')
        start_date = start_date.strftime(format='%Y-%m-%d')
        return YfScraper(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=self.__settings['timeframe']['interval']
        ).collect_data()

    def calculate_rsi(self, df: pd.DataFrame) -> float:
        period = self.__settings['rsi']

        def rma(x, n, y0):
            a = (n - 1) / n
            ak = a**np.arange(len(x) - 1, -1, -1)
            return np.r_[np.full(n, np.nan), y0, np.cumsum(
                ak * x) / ak / n + y0 * a**np.arange(1, len(x) + 1)]

        df['change'] = df['Close'].diff()
        df['gain'] = df.change.mask(df.change < 0, 0.0)
        df['loss'] = -df.change.mask(df.change > 0, -0.0)
        df['avg_gain'] = rma(df.gain[period + 1:].to_numpy(), period, np.nansum(df.gain.to_numpy()[:period + 1]) / period)
        df['avg_loss'] = rma(df.loss[period + 1:].to_numpy(), period, np.nansum(df.loss.to_numpy()[:period + 1]) / period)
        df['rs'] = df.avg_gain / df.avg_loss
        df['rsi'] = 100 - (100 / (1 + df.rs))
        rsi = round(df['rsi'][-1:].values[0], 2)
       
        return rsi

    def calculate_crossover(self, df: pd.DataFrame) -> tuple:
        # Valores dos periodos
        short_period = self.__settings['crossover']['short_period']
        long_period = self.__settings['crossover']['long_period']

        # Calculando as médias exponencial / não exponencial
        if self.__settings['crossover']['exponential'] == "True":
            df[f'MM_{short_period}'] = df['Close'].ewm(span=short_period).mean()
            df[f'MM_{long_period}'] = df['Close'].ewm(span=long_period).mean()

        else:
            df[f'MM_{short_period}'] = df['Close'].rolling(window=short_period).mean()
            df[f'MM_{long_period}'] = df['Close'].rolling(window=long_period).mean()

        # Identificando cruzamento
        df['Sinal'] = 0
        df.loc[df[f'MM_{short_period}'] > df[f'MM_{long_period}'], 'Sinal'] = 1
        df.loc[df[f'MM_{short_period}'] < df[f'MM_{long_period}'], 'Sinal'] = -1
        
        # Identificando confirmação de volume
        last_volume = df['Volume'].iloc[-1]
        volume_average = df['Volume'].tail(n=21).mean()
        check_volume = True if last_volume > volume_average else False
        
        if df['Sinal'].iloc[-1] != df['Sinal'].iloc[-2]:
            if df['Sinal'].iloc[-1] == 1:
                return "Cruzamento de alta", last_volume, check_volume 

            elif df['Sinal'].iloc[-1] == -1:
                return "Cruzamento de baixa", last_volume, check_volume

            else:
                return "-", "-", "-"
            
        else:
            return "-", "-", "-"

    def calculate_cycle(self, df: pd.DataFrame) -> str:
        short_period = self.__settings['cycle']['short_period']
        long_period = self.__settings['cycle']['long_period']
            
        # Calculando as médias móveis simples
        df[f'SMA_{short_period}'] = df['Close'].rolling(window=short_period).mean()
        df[f'SMA_{long_period}'] = df['Close'].rolling(window=long_period).mean()

        # Coletando as últimas informações
        last_close = df['Close'].iloc[-1]
        last_sma_short = df[f'SMA_{short_period}'].iloc[-1]
        last_sma_long = df[f'SMA_{long_period}'].iloc[-1]

        # Lado de compra
        if last_sma_short < last_close < last_sma_long and last_sma_short < last_sma_long:
            return "Fase de recuperação"
        elif last_close > last_sma_short and last_close > last_sma_long > last_sma_short:
            return "Fase de acumulação"
        elif last_close > last_sma_short > last_sma_long and last_close > last_sma_long:
            return "Fase de altista"

        # Lado de venda
        elif last_sma_short > last_close > last_sma_long and last_sma_short > last_sma_long:
            return "Fase de aviso"
        elif last_close < last_sma_short and last_close < last_sma_long < last_sma_short:
            return "Fase de distribuição"
        elif last_close < last_sma_short < last_sma_long and last_close < last_sma_long:
            return "Fase baixista"
        else:
            return "-"

    def create_final_dataframe(self, data: list) -> pd.DataFrame:
        columns = ['Ativo', 'Preço', 'Var. Percentual', 'Setor', 'Cruzamento', 'Ciclo', 'Volume', 'Confir. Volum.', 'RSI']
        df_final = pd.DataFrame(data=data, columns=columns)
        df_final = df_final[df_final['Cruzamento'] != '-']
        df_final = df_final[df_final['Volume'] > self.__settings['volume >']]
        return df_final

    def display_results(self, df_final: pd.DataFrame, save_file: bool) -> None:
        # os.system(command='cls' if os.name == 'nt' else 'clear')

        console.print(f"\n\n[[bold white]{self.time()}[/]] -> [[bold green]Resultado[/]]:\n\n{df_final.to_string(index=False) if not df_final.empty else "[red](Nenhuma oportunidade de investimento encontrada!)[/]"}\n")
        if save_file:
            self.save_as_file(df=df_final)

    def save_as_file(self, df: pd.DataFrame) -> None:
        save_folder = self.__settings['save_folder']
        try:
            os.mkdir(path=save_folder)
        except FileExistsError:
            pass
        filename = f'{save_folder}/Relatório de opções de investimento ({self.date()}).xlsx'
        df.to_excel(filename, index=False)
        console.print(f'[[bold yellow]Arquivo excel gerado com o resultado. ([white]{filename}[/])[/]]')

    def percentage_of_variation(self, dataframe: pd.DataFrame):
        try:
            previous_close = dataframe.iloc[-2]['Close']
            current_close = dataframe.iloc[-1]['Close']
            return round(((current_close - previous_close) / previous_close) * 100, 2)
        
        except KeyError:
            return None
