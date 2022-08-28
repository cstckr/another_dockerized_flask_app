import pyodbc
from credentials.database import server, database, username, password

driver = "{ODBC Driver 17 for SQL Server}"

connection_string_database = "DRIVER=" + driver + ";SERVER=tcp:" + server + \
    ";PORT=1433;DATABASE=" + database + ";UID=" + username + ";PWD=" + password


def sql_query_w_commit(sql_statement):
    with pyodbc.connect(connection_string_database) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            cursor.commit()


def sql_query_w_fetch(sql_statement):
    with pyodbc.connect(connection_string_database) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            query_output = cursor.fetchall()
    return query_output


def create_sql_str_get_rows_for_unlabeled_images(cur_username):
    sql_str_get_rows_for_unlabeled_images = f"""
        SELECT image_id, image_url FROM images
        WHERE image_id NOT IN (
            SELECT image_id FROM labels
            WHERE user_id = (
                SELECT user_id FROM users
                WHERE username = '{cur_username}')
                );
        """
    return sql_str_get_rows_for_unlabeled_images


def create_sql_str_get_rows_for_labeled_images(cur_username):
    sql_str_get_rows_for_labeled_images = f"""
        SELECT image_id, image_url FROM images
        WHERE image_id IN (
            SELECT image_id FROM labels
            WHERE user_id = (
                SELECT user_id FROM users
                WHERE username = '{cur_username}')
                );
        """
    return sql_str_get_rows_for_labeled_images


def create_sql_str_get_user_stats(cur_username):
    sql_str_get_user_stats = f"""
        SELECT
            COUNT(DISTINCT label_id) as count_labels,
            COUNT(DISTINCT image_id) AS count_labelled_images,
            (
                (SELECT COUNT(DISTINCT image_id) FROM images) -
                (COUNT(DISTINCT image_id))
            ) AS count_not_labelled_images
        FROM labels
        WHERE user_id = (
            SELECT user_id FROM users
            WHERE username = '{cur_username}');
        """
    return sql_str_get_user_stats


def create_sql_str_insert_label(cur_username, image_id, label):
    sql_str_insert_label = f"""
        INSERT INTO labels(user_id, image_id, label)
        VALUES (
            (
                SELECT user_id FROM users
                WHERE username = '{cur_username}'
            ),
            '{image_id}',
            '{label}')
        """
    return sql_str_insert_label
