Выбираем Apache Airflow

1. Обоснование выбора технологического решения:
    - есть готовые модули для интеграции с BigQuery, Redshift, Kafka и Spark
    - поддерживает возможность ветвления, условных операторов и event-triggers
    - можно использования из коробки fallback-logic, retry и отправку email-уведомлений
    - разаворачивание в облаке: 
      - можно выбрать GCP т.к. автоматическое развертывание - создание окружения в 1 клик через UI или gcloud и есть встроенная интеграция с BigQuery без настройки коннекторов
      - либо настрить самим в k8s, что дает полный контроль, изоляция задач, ориентировочно дешевле


# Команды на запуск
docker-compose up -d postgres

docker-compose run --rm airflow-webserver airflow db init

docker-compose run --rm airflow-webserver airflow users create \
--username admin \
--password admin \
--firstname Admin \
--lastname User \
--role Admin \
--email admin@example.com

docker-compose up -d
