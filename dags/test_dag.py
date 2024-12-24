from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator


with DAG (
    'test_dag',
    start_date = days_ago(1),
    schedule_interval = '@daily'
) as dag:
    
    thing_1 = EmptyOperator(task_id='thing_1')
    thing_2 = EmptyOperator(task_id='thing_2')
    thing_3 = EmptyOperator(task_id='thing_3')
    thing_4 = BashOperator(
        task_id='create_paste',
        bash_command="mkdir -p '/home/gustavo/Documentos/airflow-pipeline/new_paste={{data_interval_end}}'"
    )
    
    thing_1 >> [thing_2, thing_3]
    thing_3 >> thing_4