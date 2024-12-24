# Pipeline de Relatório Climático no Airflow

## Visão Geral

Este DAG do Airflow foi desenvolvido para buscar dados climáticos de uma cidade específica (Boston) utilizando a **Visual Crossing Weather API**, processar os dados e salvá-los em arquivos CSV. A pipeline é executada semanalmente, toda segunda-feira à meia-noite UTC, e organiza os dados em diretórios específicos por semana.

## Funcionalidades

- **Busca de dados climáticos** da Visual Crossing Weather API.
- **Salva dados brutos** e dois arquivos CSV processados (temperatura e condições climáticas).
- **Organiza a saída por semana**: Os dados são salvos em diretórios nomeados com a data de início da semana (`week=YYYY-MM-DD`).
- **Executa em uma agenda semanal**: O DAG é configurado para rodar toda segunda-feira à meia-noite UTC.

## Requisitos

- **Python 3.x** (preferencialmente Python 3.7 ou superior)
- **Apache Airflow**: Certifique-se de que o Airflow está corretamente instalado e em execução.
- **Pandas**: Para o processamento e salvamento dos dados em CSV.
- **Pendulum**: Para manipulação de datas e horas.
- **Chave da Visual Crossing Weather API**: Necessária para acessar os dados climáticos.

### Instalação

1. Instale os pacotes Python necessários:
   
   ```bash
   pip install apache-airflow pandas pendulum
   ```

2. Certifique-se de que você tenha acesso à **Visual Crossing Weather API**. Você precisará de uma chave de API, que pode ser obtida em [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api).

3. Configure o Airflow:
   - Configure o arquivo `airflow.cfg` adequadamente.
   - Inicialize o banco de dados do Airflow:
     ```bash
     airflow db init
     ```

4. Defina o diretório do Airflow e garanta que seu script esteja salvo na pasta `dags/` correta.

## Visão Geral do DAG

### DAG: `weather_report`

- **Data de início**: `2024-12-09`
- **Intervalo de agendamento**: `0 0 * * 1` (Toda segunda-feira à meia-noite UTC)
- **Fuso horário**: UTC

### Tarefas

1. **create_paste** (`BashOperator`):
   - Esta tarefa cria um diretório para os dados da semana atual, utilizando a variável `data_interval_end` do Airflow para definir o nome do diretório (no formato `week=YYYY-MM-DD`).
   
   ```bash
   mkdir -p '/home/gustavo/Documentos/airflow-pipeline/week={{data_interval_end.strftime('%Y-%m-%d')}}'
   ```

2. **get_weather_info** (`PythonOperator`):
   - Esta tarefa chama a função `get_info` para buscar os dados climáticos de Boston na Visual Crossing Weather API.
   - A função processa os dados e os divide em três arquivos CSV:
     - `raw_data.csv` (conjunto completo de dados)
     - `temperature.csv` (dados relacionados à temperatura)
     - `conditions.csv` (dados relacionados às condições climáticas)
   - Os dados processados são salvos no diretório criado pela primeira tarefa.

   ### Função Python `get_info`:
   A função busca os dados climáticos para a semana atual (de `data_interval_end` a `data_interval_end + 7 dias`) e processa os dados em três arquivos CSV.

   ```python
   def get_info(data_interval_end):
       city = 'Boston'
       key = '2UZ75GM2TYG3ALLHWA7GSKUHM'  # Sua chave de API aqui
       URL = join("https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/",
                  f"{city}/{data_interval_end}/{ds_add(data_interval_end, 7)}?unitGroup=metric&include=days&key={key}&contentType=csv")

       data = pd.read_csv(URL)
       print(data.head())

       file_path = f'/home/gustavo/Documentos/airflow-pipeline/week={data_interval_end}/'

       data.to_csv(file_path + 'raw_data.csv')
       data[['datetime','tempmin', 'temp', 'tempmax']].to_csv(file_path + 'temperature.csv')
       data[['datetime', 'description', 'icon']].to_csv(file_path + 'conditions.csv')
   ```

## Como Funciona

### 1. Execução do DAG

- **Agendamento**: O DAG é executado toda segunda-feira à meia-noite UTC (`0 0 * * 1`).
- **Tarefa 1 (`create_paste`)**: Cria um novo diretório para armazenar os arquivos de dados da semana, com base na variável `data_interval_end` (que representa o final do intervalo de dados da execução atual do DAG).
- **Tarefa 2 (`get_weather_info`)**: Busca os dados climáticos para Boston, processa-os em três arquivos CSV e os salva no diretório criado na tarefa 1.

### 2. Fluxo de Dados

1. Na primeira tarefa, um diretório é criado com o nome baseado no parâmetro `data_interval_end`, que representa o final do intervalo de dados para a execução atual do DAG.
   
2. A segunda tarefa utiliza `data_interval_end` para buscar os dados climáticos de Boston para a semana atual (do `data_interval_end` até `data_interval_end + 7 dias`).

3. Os dados recebidos são processados e divididos em:
   - `raw_data.csv` (conjunto completo de dados).
   - `temperature.csv` (colunas relacionadas à temperatura: `datetime`, `tempmin`, `temp`, `tempmax`).
   - `conditions.csv` (colunas relacionadas às condições climáticas: `datetime`, `description`, `icon`).

4. Os arquivos CSV processados são salvos no diretório criado pela primeira tarefa.

## Configuração

### Parâmetros

- `data_interval_end`: A data que representa o final do intervalo de dados para a execução atual do DAG. Este valor é passado para a função `get_info` para gerar a URL da API e processar os dados.

### Variáveis/Conexões do Airflow

Certifique-se de definir o seguinte:
- **Chave da API do Weather**: Armazene sua chave da Visual Crossing Weather API como uma variável do Airflow ou diretamente no código (não recomendado para produção).
- **Diretório do Airflow**: Configure o diretório onde os DAGs e logs serão armazenados.

## Estrutura de Diretórios

A estrutura de diretórios gerada será:

```
/home/gustavo/Documentos/airflow-pipeline/
  └── week=2024-12-09/
      ├── raw_data.csv
      ├── temperature.csv
      └── conditions.csv
```

A cada semana, um novo diretório será criado com a respectiva data e os arquivos CSV serão salvos nele.

## Melhorias Possíveis

- **Tratamento de Erros**: Adicionar blocos `try-except` para lidar com falhas nas requisições à API ou erros ao salvar os arquivos CSV.
- **Logs**: Melhorar o logging para monitorar o sucesso ou falha das tarefas.
- **Entrada Dinâmica de Cidades**: Modificar o script para buscar dados de diferentes cidades com base em entradas dinâmicas ou variáveis do Airflow.
- **Paralelismo de Tarefas**: Permitir execução paralela para buscar dados de múltiplas cidades ou diferentes datas.

## Licença

Este projeto é licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

