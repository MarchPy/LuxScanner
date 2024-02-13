# **LuxScanner & Fundamentus Scraper - Análise Integrada**

## LuxScanner - Ferramenta de Análise de Ações

LuxScanner é uma ferramenta avançada em Python para análise de mercado de ações, incorporando estratégias de investimento por meio de indicadores técnicos. A ferramenta é configurada usando um arquivo JSON que oferece flexibilidade e controle sobre os ativos a serem analisados, os setores de interesse e os parâmetros de estratégia.

**Configuração do Arquivo JSON:**

O arquivo de configuração, localizado em 'config/tickers.json', é estruturado para permitir uma personalização abrangente. Os principais elementos incluem:

1. **Setores e Ativos:**

   - Defina setores de interesse, cada um com um nome, status de coleta e uma lista de ativos associados.
   - Controle se a coleta de dados é permitida para cada setor, ajustando o status para "True" ou "False".
2. **Intervalo de Tempo:**

   - Configure o intervalo de tempo para coleta de dados, especificando o período e o intervalo desejados.
3. **Estratégia RSI:**

   - Ajuste o período para o cálculo do RSI (Relative Strength Index) conforme suas preferências.
4. **Cruzamento de Médias:**

   - Configure os períodos curto e longo para o cruzamento de médias móveis.
   - Escolha entre médias exponenciais ou não exponenciais.

**Funcionalidades Principais:**

- **Coleta de Dados Dinâmica:**

  - A ferramenta coleta dinamicamente dados do Yahoo Finance para os ativos especificados print(argv)no arquivo de configuração.
- **Análise de Estratégia:**

  - Utiliza uma estratégia de investimento que considera cruzamento de médias móveis, RSI e análise de volume para identificar oportunidades de investimento.
- **Limiares Configuráveis:**

  - Estabeleça limiares para o volume, personalizando a análise com base em suas preferências.
- **Relatórios Detalhados:**

  - Os resultados da análise são apresentados em um relatório Excel, destacando cruzamentos de médias, valores de RSI e volumes médios ao longo de um período específico.

**Para salvar o resultado em um arquivo execute o programa utilizando o parâmetro** `-s`

Exemplo:

```bash
python3 run.py -s
```

Essa abordagem personalizável e abrangente permite que investidores ajustem facilmente a estratégia de acordo com suas preferências e objetivos financeiros. Experimente o LuxScanner para aprimorar suas decisões de investimento com análises técnicas avançadas.

## Fundamentus Scraper - Análise Fundamentalista Simplificada

O Fundamentus Scraper é uma ferramenta Python que simplifica a análise fundamentalista de uma lista extensa de ações brasileiras. Utilizando a biblioteca requests e pandas, a ferramenta busca automaticamente dados financeiros importantes do site Fundamentus para os tickers fornecidos.

**Características Principais:**

- **Lista de Ações Padrão:**

  - O código vem pré-configurado com uma lista abrangente de tickers de ações brasileiras, abrangendo uma variedade de setores.
- **Coleta Dinâmica de Dados:**

  - A ferramenta acessa o site Fundamentus para cada ticker, coletando informações cruciais sobre a empresa.
- **Tratamento de Dados:**

  - Os dados coletados são organizados em um DataFrame do Pandas, tornando-os fáceis de manipular e analisar.
- **Formatação Adequada:**

  - A ferramenta realiza a conversão e formatação adequada de dados, garantindo que os valores estejam prontos para análise.
- **Exportação para Excel:**

  - Os resultados finais são exportados para um arquivo Excel chamado "Fundamentus.xlsx", fornecendo uma visão consolidada e organizada das métricas fundamentais das ações.

**Como Usar:**

1. Execute o código para realizar a coleta de dados fundamentalistas para os tickers fornecidos.
2. O arquivo Excel resultante, "Fundamentus.xlsx", conterá informações detalhadas sobre cada empresa, facilitando análises mais aprofundadas.

Este script simplifica o processo de obtenção de dados fundamentais, fornecendo uma visão rápida e organizada das métricas importantes para auxiliar nas decisões de investimento. Experimente o LuxScanner e o Fundamentus Scraper para uma análise abrangente e integrada do mercado financeiro.
