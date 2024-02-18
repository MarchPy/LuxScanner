from sys import argv
from rich.console import Console
from src.LuxScanner import LuxScanner
from src.FundamentusScraper import Main


console = Console()


if __name__ == "__main__":
    try: 
        if len(argv) > 1 and "--fundamentus" in argv:
            app = Main()
            app.main(save_file=True if len(argv) > 1 and '-s' in argv else False)

        else:
            app = LuxScanner()
            app.collect_data_from_json_file(save_file=True if len(argv) > 1 and '-s' in argv else False)

    except KeyboardInterrupt:
        console.print('[[italic bold yellow]Processo encerrado pelo usuário!!![/]]')
