
# **LuxScanner - Ferramenta de Análise de Ações**

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
  - A ferramenta coleta dinamicamente dados do Yahoo Finance para os ativos especificados no arquivo de configuração.
  
- **Análise de Estratégia:**
  - Utiliza uma estratégia de investimento que considera cruzamento de médias móveis, RSI e análise de volume para identificar oportunidades de investimento.
 
- **Limiares Configuráveis:**
  - Estabeleça limiares para o volume, personalizando a análise com base em suas preferências. 

- **Relatórios Detalhados:**
  - Os resultados da análise são apresentados em um relatório Excel, destacando cruzamentos de médias, valores de RSI e volumes médios ao longo de um período específico.

Essa abordagem personalizável e abrangente permite que investidores ajustem facilmente a estratégia de acordo com suas preferências e objetivos financeiros. Experimente o LuxScanner para aprimorar suas decisões de investimento com análises técnicas avançadas.
