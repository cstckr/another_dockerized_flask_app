from flask_bcrypt import Bcrypt
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import tensorflow as tf
from PIL import Image
from credentials.blob_storage import (connection_string_blob, container_name,
                                      storage_account_name)
from os import walk
from extra.database_accessories import sql_query_w_commit

# %% Database functionality


# Users table
def create_sql_str_insert_user(username, password):
    flask_bcrypt = Bcrypt()
    pw_hash = flask_bcrypt.generate_password_hash(password).decode("utf-8")
    sql_insert_user = f"""
        INSERT INTO users(username, password)
        VALUES ('{username}', '{pw_hash}')
        """
    return sql_insert_user


def create_sql_str_drop_table(table_name):
    sql_str_drop_table = f"DROP TABLE IF EXISTS {table_name}"
    return sql_str_drop_table


sql_str_create_users_table = """
    IF OBJECT_ID(N'users', N'U') IS NULL
    BEGIN
    CREATE TABLE users
        (
        user_id INT IDENTITY PRIMARY KEY,
        username NVARCHAR(128) NOT NULL UNIQUE,
        password NVARCHAR(75) NOT NULL,
        )
    END;
    """


# Images
sql_str_create_images_table = """
    IF OBJECT_ID(N'images', N'U') IS NULL
    BEGIN
    CREATE TABLE images
        (
        image_id INT IDENTITY PRIMARY KEY,
        image_url NVARCHAR(128) NOT NULL UNIQUE,
        )
    END;
    """


def create_sql_str_insert_image(image_url):
    sql_insert_image_url = f"""
        INSERT INTO images(image_url)
        VALUES ('{image_url}')
        """
    return sql_insert_image_url


# Labels
sql_str_create_labels_table = """
    IF OBJECT_ID(N'labels', N'U') IS NULL
    BEGIN
    CREATE TABLE labels
        (
        label_id INT IDENTITY PRIMARY KEY,

        image_id INT FOREIGN KEY REFERENCES images(image_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        user_id INT FOREIGN KEY REFERENCES users(user_id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        label TINYINT,
        )
    END;
    """


# %% Create database tables

sql_query_w_commit(create_sql_str_drop_table("labels"))

sql_query_w_commit(create_sql_str_drop_table("users"))
sql_query_w_commit(sql_str_create_users_table)
sql_query_w_commit(create_sql_str_insert_user("guest1", "123456"))
sql_query_w_commit(create_sql_str_insert_user("guest2", "123456"))
sql_query_w_commit(create_sql_str_insert_user("guest3", "123456"))

sql_query_w_commit(create_sql_str_drop_table("images"))
sql_query_w_commit(sql_str_create_images_table)

sql_query_w_commit(sql_str_create_labels_table)

# %% Download some dummy images

file_dir_local = "./images/"

# Get dummy images and save them locally
(train_images, _), (_, _) = tf.keras.datasets.mnist.load_data()

for i in range(200):
    image = Image.fromarray(train_images[i])
    image.save(file_dir_local + f"{i}.jpg")


# %% Upload images to Azure blob storage and create entries in images table

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string_blob)

filenames = next(walk(file_dir_local), (None, None, []))[2]
# See: https://stackoverflow.com/questions/58164698/azure-server-failed-to-authenticate-the-request/67679100#67679100
file_dir_azure = file_dir_local.replace("./", "")

file_paths_azure = [(file_dir_azure + file) for file in filenames]


for file_path_azure in file_paths_azure[0:200]:
    # Push images to blob storage
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=file_path_azure)
        with open(file_path_azure, "rb") as data:
            blob_client.upload_blob(data)
    except ResourceExistsError:
        print(f"{file_path_azure} already exists.")

    # Push image links to the database
    try:
        blob_url = "https://" + storage_account_name + \
            ".blob.core.windows.net/" + container_name + "/" + file_path_azure
        sql_query_w_commit(create_sql_str_insert_image(blob_url))
    except BaseException as e:
        print(e)
