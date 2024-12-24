import os
import pandas as pd # type: ignore
from os.path import join
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.macros import ds_add
import pendulum
from airflow.utils.dates import days_ago
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

with DAG (
    'weather_report',
    start_date=pendulum.datetime(2024, 12, 9, tz="UTC"),
    schedule_interval='0 0 * * 1',
) as dag:
    
    task_1 = BashOperator(
        task_id='create_paste',
        bash_command="mkdir -p '/home/gustavo/Documentos/airflow-pipeline/week={{data_interval_end.strftime('%Y-%m-%d')}}'"
    )
    
    def get_info(data_interval_end):
        city = 'Boston'
        key = '2UZ75GM2TYG3ALLHWA7GSKUHM'

        URL = join("https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/",
                f"{city}/{data_interval_end}/{ds_add(data_interval_end, 7)}?unitGroup=metric&include=days&key={key}&contentType=csv")


        data = pd.read_csv(URL)
        print(data.head())

        file_path = f'/home/gustavo/Documentos/airflow-pipeline/week={data_interval_end}/'

        data.to_csv(file_path + 'raw_data.csv')
        data[['datetime','tempmin', 'temp', 'tempmax']].to_csv(file_path + 'temperature.csv')
        data[['datetime', 'description', 'icon']].to_csv(file_path + 'conditions.csv')
   
    task_2 = PythonOperator(
        task_id='get_weather_info',
        python_callable=get_info,
        op_kwargs= {'data_interval_end': '{{data_interval_end.strftime("%Y-%m-%d")}}'}
    )
    
    task_1 >> task_2