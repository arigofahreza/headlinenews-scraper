import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("Current dir:", current_dir)
print("Python path:", sys.path)

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from parsers.cnn_parser import parse_cnn
from parsers.detiknews_parser import parse_detiknews
from parsers.kompas_parser import parse_kompas
from parsers.liputan6_parser import parse_liputan6
from parsers.tribun_parser import parse_tribun

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        dag_id='news_scraper_dag',
        default_args=default_args,
        schedule='@daily',
        start_date=datetime(2025, 10, 1),
        catchup=False,
        tags=['news', 'scraper'],
) as dag:
    cnn_task = PythonOperator(
        task_id='scrap_cnn',
        python_callable=parse_cnn,
    )

    detik_task = PythonOperator(
        task_id='scrap_detiknews',
        python_callable=parse_detiknews,
    )

    kompas_task = PythonOperator(
        task_id='scrap_kompas',
        python_callable=parse_kompas,
    )

    liputan6_task = PythonOperator(
        task_id='scrap_liputan6',
        python_callable=parse_liputan6,
    )

    tribun_task = PythonOperator(
        task_id='scrap_tribun',
        python_callable=parse_tribun,
    )

    [cnn_task, detik_task, kompas_task, liputan6_task, tribun_task]
