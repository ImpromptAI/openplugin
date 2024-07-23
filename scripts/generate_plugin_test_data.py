import json
import os

import pymysql
import requests
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    environment = os.environ["ENVIRONMENT"]

    if environment == "production":
        host = os.environ["PROD_DB_HOSTNAME"]
        user = os.environ["PROD_DB_USERNAME"]
        password = os.environ["PROD_DB_PASSWORD"]
    elif environment == "beta":
        host = os.environ["BETA_DB_HOSTNAME"]
        user = os.environ["BETA_DB_USERNAME"]
        password = os.environ["BETA_DB_PASSWORD"]
    else:
        host = os.environ["DEV_DB_HOSTNAME"]
        user = os.environ["DEV_DB_USERNAME"]
        password = os.environ["DEV_DB_PASSWORD"]

    if host is not None and user is not None and password is not None:
        try:
            db = pymysql.connect(
                user=user,
                password=password,
                host=host,
                cursorclass=pymysql.cursors.DictCursor,
            )
            return db
        except Exception as e:
            print(e)
            raise Exception("Unable to connect to db")
    else:
        raise Exception("DB environment variables are not setup")


def start():
    environment = os.environ["ENVIRONMENT"]
    filename = f"test_plugins_{environment}.json"
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM imprompt_management.plugins;")
    rows = cursor.fetchall()

    values = []
    for row in rows:
        try:
            print(f"RUNNING FOR: {row['name']}")
            openplugin_manifest_url = row["openplugin_manifest_url"]
            openplugin_manifest_json = requests.get(openplugin_manifest_url).json()
            openplugin_function_count = 0
            plugin_operation_map = openplugin_manifest_json.get("plugin_operations", {})
            examples = []
            for path in plugin_operation_map.keys():
                for method in plugin_operation_map[path].keys():
                    openplugin_function_count += 1
                    for example in plugin_operation_map[path][method].get(
                        "human_usage_examples", []
                    ):
                        examples.append(
                            {
                                "path": path,
                                "method": method,
                                "example": example,
                            }
                        )

            openapi_doc_url = row["openapi_doc_url"]
            openapi_doc_json = requests.get(openapi_doc_url).json()
            openapi_function_count = 0

            for path in openapi_doc_json["paths"].keys():
                for method in openapi_doc_json["paths"][path].keys():
                    if method.lower() in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                        "head",
                        "options",
                        "x-amazon-apigateway-any-method",
                    ]:
                        openapi_function_count += 1

            values.append(
                {
                    "openplugin_manifest_url": row["openplugin_manifest_url"],
                    "openapi_doc_url": row["openapi_doc_url"],
                    "openplugin_function_count": openplugin_function_count,
                    "examples": examples,
                    "openapi_function_count": openapi_function_count,
                }
            )
        except Exception:
            print("=-=-=-=-=-=")
            print(f"FAILED FOR: {row['name']}")
            print("=-=-=-=-=-=")

    with open(f"tests/resources/{filename}", "w") as f:
        f.write(json.dumps(values))
    db.close()


start()
