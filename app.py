from flask import Flask, render_template
from time import sleep
import boto3

app = Flask(__name__)

from flask import Flask, render_template
import os
from time import sleep
from boto3 import client


os.environ["AWS_ACCESS_KEY_ID"] = 'AKIAV7RY5NII44HEILLU'
os.environ["AWS_SECRET_ACCESS_KEY"] = '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'
os.environ["AWS_DEFAULT_REGION"] = 'eu-north-1'

athena_client = client('athena', region_name='eu-north-1', aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])


app = Flask(__name__)

RESULT_OUTPUT_LOCATION = "s3://client-prediction-glue-temporary/results/output.csv"

def has_query_succeeded(execution_id):
    state = "RUNNING"
    max_execution = 5

    while max_execution > 0 and state in ["RUNNING", "QUEUED"]:
        max_execution -= 1
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        if (
            "QueryExecution" in response
            and "Status" in response["QueryExecution"]
            and "State" in response["QueryExecution"]["Status"]
        ):
            state = response["QueryExecution"]["Status"]["State"]
            if state == "SUCCEEDED":
                return True

        sleep(30)

def get_rows():
    query = 'SELECT * FROM "kafka-customers-prediction-database"."kafka_customers_prediction_project_najlae" limit 10;'
    response = athena_client.start_query_execution(
        QueryString=query,
        ResultConfiguration={"OutputLocation": RESULT_OUTPUT_LOCATION}
    )

    return response["QueryExecutionId"]

def get_query_results(execution_id):
    response = athena_client.get_query_results(
    QueryExecutionId=execution_id
    )

    results = response['ResultSet']['Rows']
    return results

def get_num_rows():
    query = 'SELECT COUNT(*) AS NR FROM "kafka-customers-prediction-database"."kafka_customers_prediction_project_najlae" limit 10;'
    response = athena_client.start_query_execution(
        QueryString=query,
        ResultConfiguration={"OutputLocation": RESULT_OUTPUT_LOCATION}
    )

    return response["QueryExecutionId"]

@app.route('/')
def index():
    data_list = []  # List to store results

    while True:
        execution_id = get_rows()
        print(f"Get Rows execution id: {execution_id}")

        query_status = has_query_succeeded(execution_id)
        print(f"Query state: {query_status}")

        if query_status:
            results = get_query_results(execution_id=execution_id)
            # Extracting the header and data
            header = results[0]['Data']
            data = results[1:]

            # Mapping header and data to create a dictionary
            result_dict_list = []
            for row in data:
                result_dict = {}
                for i, field in enumerate(header):
                    key = field['VarCharValue'].lower().replace(' ', '_')
                    value = row['Data'][i]['VarCharValue']
                    result_dict[key] = value
                result_dict_list.append(result_dict)

            # Adding results to the data list
            data_list.extend(result_dict_list)
            print(data_list)

        # Wait for 5 seconds before checking again
        sleep(5)
        return render_template('index.html', data=data_list)

    

if __name__ == '__main__':
    app.run(debug=True)


data_list = []  # List to store results

while True:
    execution_id = get_rows()
    print(f"Get Rows execution id: {execution_id}")

    query_status = has_query_succeeded(execution_id)
    print(f"Query state: {query_status}")

    if query_status:
        results = get_query_results(execution_id=execution_id)
        # Extracting the header and data
        header = results[0]['Data']
        data = results[1:]

        # Mapping header and data to create a dictionary
        result_dict_list = []
        for row in data:
            result_dict = {}
            for i, field in enumerate(header):
                key = field['VarCharValue'].lower().replace(' ', '_')
                value = row['Data'][i]['VarCharValue']
                result_dict[key] = value
            result_dict_list.append(result_dict)

        # Adding results to the data list
        data_list.extend(result_dict_list)
        print(data_list)

    # Wait for 5 seconds before checking again
    sleep(5)


