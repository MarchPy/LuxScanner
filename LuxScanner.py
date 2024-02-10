import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from sys import argv
from datetime import datetime
from rich.console import Console


console = Console()


# Função para retornar o horário atual
def time():
    return datetime.now().strftime(format='%H:%M:%S')


# Função para retornar a data atual
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

    def colect_data_from_json_file(self, save_file=False):
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

                    # Verificando se o DataFrame não está vázio para realizar o calculo de indicadores
                    if not df_yf.empty:
                        # Coletando alguns indicadores 
                        rsi = self.rsi(df=df_yf)
                        crossover, volume, check_volume = self.crossover(df=df_yf)
                        cycle = self.cycle(df=df_yf)
                        data.append([ticker, sector_name, crossover, volume, check_volume, cycle, rsi])
        
        # Definindo o DataFrame final
        columns = ['Ativo', 'Setor', 'Cruzamento', 'Volume', 'Vl. Confir.', 'Ciclo', 'RSI']
        df_final = pd.DataFrame(data=data, columns=columns)
        df_final = df_final[df_final['Cruzamento'] != '-']
        df_final = df_final[df_final['Volume'] > self.data_tickers['volume >']]
        
        # Exibição de resultado
        os.system(command='cls' if os.name == 'nt' else 'clear')
        console.print(f"[[bold white]{time()}[/]] -> [[bold green]Resultado[/]]:\n\n{str(df_final) if not df_final.empty else "[red]Tabela vázia (Nemhuma oportunidade de investimento encontrada)[/]"}\n")
        
        if save_file:
            self.save_as_file(df=df_final)

    def rsi(self, df: pd.DataFrame):
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
        
        return rsi
    
    def crossover(self, df: pd.DataFrame):
        # Valores dos periodos
        short_period = self.data_tickers['crossover']['short_period']
        long_period = self.data_tickers['crossover']['long_period']

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
    
    def cycle(self, df: pd.DataFrame):
        short_period = self.data_tickers['cycle']['short_period']
        long_period = self.data_tickers['cycle']['long_period']
            
        # Calculando as médias móveis simples
        df[f'SMA_{short_period}'] = df['Close'].rolling(window=short_period).mean()
        df[f'SMA_{long_period}'] = df['Close'].rolling(window=long_period).mean()

        # Coletando as últimas informações
        last_close = df['Close'].iloc[-1]
        last_sma_short = df[f'SMA_{short_period}'].iloc[-1]
        last_sma_long = df[f'SMA_{long_period}'].iloc[-1]

        # Fazendo o filtro
        # Lado de compras
        if last_close > last_sma_short and last_close < last_sma_long and last_sma_short < last_sma_long: return "Fase de recuperação"
        elif last_close > last_sma_short and last_close > last_sma_long and last_sma_short < last_sma_long: return "Fase de acumulação"
        elif last_close > last_sma_short and last_close > last_sma_long and last_sma_short > last_sma_long: return "Fase altista"

        # Lado de vendas
        elif last_close > last_sma_short and last_close > last_sma_long and last_sma_short > last_sma_long: return "Fase de aviso"
        elif last_close < last_sma_short and last_close < last_sma_long and last_sma_short > last_sma_long: return "Fase de distribuição"
        elif last_close < last_sma_short and last_close < last_sma_long and last_sma_short < last_sma_long: return "Fase baixista"

        else: return "-"
        
    def save_as_file(self, df: pd.DataFrame):
        # Criando a pasta onde seram salvos os arquivos
        save_folder = self.data_tickers['save_folder']
        try:
            os.mkdir(path=save_folder)
        
        except FileExistsError:
            pass
        
        filename = f'{save_folder}Relatório de opções de investimento ({date()}).xlsx'
        df.to_excel(filename, index=False)
        console.print(f'[[bold yellow]Arquivo excel gerado com o resultado. ([white]{filename}[/])[/]]')


if __name__ == "__main__":
    try:        
        app = LuxScanner()
        app.colect_data_from_json_file(save_file=True if len(argv) > 1 and argv[1] == '-s' else False)

    except KeyboardInterrupt:
        console.print('[[italic bold yellow]Processo encerrado pelo usuário!!![/]]')
