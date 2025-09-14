FROM openjdk:24-slim
# 8080
WORKDIR .
COPY build/libs/*.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]

#drop table batch_job_execution, batch_job_execution_context, batch_job_execution_params, batch_job_instance, batch_step_execution, batch_step_execution_context;
#truncate table loyality_data, products;
