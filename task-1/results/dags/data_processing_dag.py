from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.email import send_email
from airflow.exceptions import AirflowException
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'email': ['your_email@gmail.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'start_date': datetime(2023, 1, 1),
}

def success_email_function(context):
    subject = f"Airflow DAG {context['dag'].dag_id} Success"
    body = f"""
    DAG {context['dag'].dag_id} completed successfully!

    Execution Date: {context['execution_date']}
    Task Instance: {context['task_instance_key_str']}
    """

    send_email(
        to=default_args['email'],
        subject=subject,
        html_content=body
    )

def failure_email_function(context):
    subject = f"Airflow DAG {context['dag'].dag_id} Failed"
    body = f"""
    DAG {context['dag'].dag_id} failed!

    Execution Date: {context['execution_date']}
    Task Instance: {context['task_instance_key_str']}
    Exception: {context.get('exception')}
    """

    send_email(
        to=default_args['email'],
        subject=subject,
        html_content=body
    )

def read_data_from_file(**kwargs):
    try:

        file_path = '/opt/airflow/data/sample_data.csv'
        df = pd.read_csv(file_path)


        kwargs['ti'].xcom_push(key='dataframe', value=df.to_json())

        logging.info(f"Successfully read data from {file_path}")
        logging.info(f"Data shape: {df.shape}")

        return "Data read successfully"
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        raise AirflowException(f"Failed to read data: {e}")

def analyze_data(**kwargs):
    try:

        ti = kwargs['ti']
        data_json = ti.xcom_pull(key='dataframe', task_ids='read_data')
        df = pd.read_json(data_json)


        mean_value = df['value'].mean()
        logging.info(f"Mean value: {mean_value}")

        # Сохраняем результат анализа
        ti.xcom_push(key='mean_value', value=mean_value)


        if mean_value > 50:
            return 'high_value_branch'
        else:
            return 'low_value_branch'

    except Exception as e:
        logging.error(f"Error analyzing data: {e}")
        raise AirflowException(f"Failed to analyze data: {e}")

def process_high_value(**kwargs):
    try:
        ti = kwargs['ti']
        mean_value = ti.xcom_pull(key='mean_value', task_ids='analyze_data')
        logging.info(f"Processing high value data: {mean_value}")


        if kwargs.get('test_failure', False):
            raise ValueError("Simulated failure for testing retry")

        return "High value processing completed"
    except Exception as e:
        logging.error(f"Error in high value processing: {e}")
        raise AirflowException(f"High value processing failed: {e}")

def process_low_value(**kwargs):
    try:
        ti = kwargs['ti']
        mean_value = ti.xcom_pull(key='mean_value', task_ids='analyze_data')
        logging.info(f"Processing low value data: {mean_value}")
        return "Low value processing completed"
    except Exception as e:
        logging.error(f"Error in low value processing: {e}")
        raise AirflowException(f"Low value processing failed: {e}")

def final_processing(**kwargs):
    try:
        logging.info("Final processing step")
        return "Pipeline completed successfully"
    except Exception as e:
        logging.error(f"Error in final processing: {e}")
        raise AirflowException(f"Final processing failed: {e}")

with DAG(
    'data_processing_pipeline',
    default_args=default_args,
    description='A data processing pipeline with branching and email notifications',
    schedule_interval=timedelta(days=1),
    catchup=False,
    on_success_callback=success_email_function,
    on_failure_callback=failure_email_function,
) as dag:

    start = DummyOperator(task_id='start')

    read_data = PythonOperator(
        task_id='read_data',
        python_callable=read_data_from_file,
        retries=2,
        retry_delay=timedelta(minutes=2),
        execution_timeout=timedelta(minutes=5),
    )

    analyze_data_task = BranchPythonOperator(
        task_id='analyze_data',
        python_callable=analyze_data,
        retries=1,
        retry_delay=timedelta(minutes=1),
    )

    high_value_branch = PythonOperator(
        task_id='high_value_branch',
        python_callable=process_high_value,
        retries=3,
        retry_delay=timedelta(minutes=1),
    )

    low_value_branch = PythonOperator(
        task_id='low_value_branch',
        python_callable=process_low_value,
        retries=2,
        retry_delay=timedelta(minutes=1),
    )

    final_task = PythonOperator(
        task_id='final_processing',
        python_callable=final_processing,
        retries=1,
        retry_delay=timedelta(minutes=1),
    )

    end = DummyOperator(task_id='end', trigger_rule='none_failed')


    start >> read_data >> analyze_data_task
    analyze_data_task >> high_value_branch >> final_task
    analyze_data_task >> low_value_branch >> final_task
    final_task >> end
