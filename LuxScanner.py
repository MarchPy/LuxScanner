import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from rich.console import Console


console = Console()


def time():
    return datetime.now().strftime(format='%H:%M:%S')


def date():
    return datetime.now().strftime(format='%d-%m-%Y')


class LuxScanner:
    def __init__(self) -> None:
        try:
            # Abrindo o arquivo json com os dados
            with open(file='config/tickers.json', mode='r', encoding='utf-8') as file_obj:
                self.data_tickers = json.load(file_obj)

        except FileNotFoundError:
            pass

    def colect_data_from_json_file(self):
        # Resultado final
        data = []

        # Coletando dados por setor
        for sector in self.data_tickers['sectors']:
            sector_name = sector['name']
            status_colect = sector['status']
            tickers = sector['tickers']

            # Verificando se foi permitido a coleta de dados dos ativos do setor
            if status_colect == "True":
                for ticker in tickers:
                    console.print(f"[[bold blue]{time()}[/]] -> [Setor: [bold yellow]{sector_name}[/]] [[italic white]Coletando dados do ativo[/]] :: {ticker}")
                    df_yf = yf.Ticker(ticker=ticker + ".SA").history(
                        period=self.data_tickers['timeframe']['period'],
                        interval=self.data_tickers['timeframe']['interval']
                    )

                    if not df_yf.empty:
                        result = self.strategy(df=df_yf)
                        if result is not None:
                            close = round(df_yf['Close'].iloc[-1], 2)
                            crossover, rsi, volume, check_volume = result
                            data.append([ticker, close, sector_name, crossover, rsi, volume, check_volume])

        self.save_as_file(data=data)

    def strategy(self, df: pd.DataFrame):
        volume = int(df['Volume'].tail(n=21).mean())
        if volume > self.data_tickers['volume >']:
            
            # Calculando RSI
            period = self.data_tickers['rsi']

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

            # Valores dos periodos
            short_period = self.data_tickers['crossover']['short period']
            long_period = self.data_tickers['crossover']['long period']

            # Calculando as médias exponencial/não exponencial
            if self.data_tickers['crossover']['exponential'] == "True":
                df[f'MM_{short_period}'] = df['Close'].ewm(span=short_period).mean()
                df[f'MM_{long_period}'] = df['Close'].ewm(span=long_period).mean()

            else:
                df[f'MM_{short_period}'] = df['Close'].rolling(window=short_period).mean()
                df[f'MM_{long_period}'] = df['Close'].rolling(window=long_period).mean()

            # Identificando cruzamento
            df['Sinal'] = 0
            df.loc[df[f'MM_{short_period}'] > df[f'MM_{long_period}'], 'Sinal'] = 1
            df.loc[df[f'MM_{short_period}'] < df[f'MM_{long_period}'], 'Sinal'] = -1
            
            check_volume = 'Sim' if df['Volume'].iloc[-1] > volume else 'Não'

            if df['Sinal'].iloc[-1] != df['Sinal'].iloc[-2]:
                if df['Sinal'].iloc[-1] == 1:
                    return ["Cruzamento de alta", rsi, volume, check_volume]

                elif df['Sinal'].iloc[-1] == -1:
                    return ["Cruzamento de baixa", rsi, volume, check_volume]

                else:
                    return

            else:
                return

    def save_as_file(self, data: list):
        save_folder = self.data_tickers['save_folder']
        try:
            os.mkdir(path=save_folder)
        
        except FileExistsError:
            pass
        
        columns = ['Ativo', 'Vl. de Fechamento', 'Setor', 'Cruzamento', 'RSI', 'Vol. Méd. 21p', 'Confir. Volume']
        df = pd.DataFrame(data=data, columns=columns)
        os.system(command='cls' if os.name == 'nt' else 'clear')
        console.print(f"[[bold white]{time()}[/]] -> [[bold green]Resultado[/]]:\n\n{df if not df.empty else "[red]Tabela vázia (Nemhuma oportunidade de investimento encontrada)[/]"}\n")
        filename = f'{save_folder}Relatório de opções de investimento ({date()}).xlsx'
        df.to_excel(filename, index=False)
        console.print(f'[[bold yellow]Arquivo excel gerado com o resultado. ({filename})[/]]')

if __name__ == "__main__":
    try:
        app = LuxScanner()
        app.colect_data_from_json_file()

    except KeyboardInterrupt:
        console.print('[[italic bold yellow]Processo encerrado pelo usuário!!![/]]')
