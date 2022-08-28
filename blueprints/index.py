from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash)
from flask_login import login_required, current_user
from extra.database_accessories import (
    sql_query_w_fetch, sql_query_w_commit, create_sql_str_get_user_stats,
    create_sql_str_get_rows_for_unlabeled_images,
    create_sql_str_get_rows_for_labeled_images,
    create_sql_str_insert_label)
from credentials.blob_storage import sas_tocken
import numpy as np
import random


index = Blueprint("index", __name__)


@index.route("/main", methods=["GET", "POST"])
@login_required
def main():
    count_labels, count_labeled_images, count_not_labeled_images = \
        sql_query_w_fetch(
            create_sql_str_get_user_stats(current_user.username))[0]

    if count_not_labeled_images == 0:
        flash("There are currently no more images to label.")
        return redirect(url_for("authentication.logout"))

    # With 20% chance, an image that has already been labeld by the user
    # will be served for labeling again.
    serve_unlabeled_image = np.random.choice(
        np.array([True, False]), 1, p=[0.8, 0.2])[0]

    if (count_labels == 0) | serve_unlabeled_image:
        rows_images = sql_query_w_fetch(
            create_sql_str_get_rows_for_unlabeled_images(
                current_user.username))
        row_image = random.choice(rows_images)
        session["curent_image_id"] = row_image[0]
        url = row_image[1] + "?" + sas_tocken
    elif (~serve_unlabeled_image):
        rows_images = sql_query_w_fetch(
            create_sql_str_get_rows_for_labeled_images(
                current_user.username))
        row_image = random.choice(rows_images)
        session["curent_image_id"] = row_image[0]
        url = row_image[1] + "?" + sas_tocken
    return render_template("main.html",
                           url=url,
                           username=current_user.username,
                           count_labels=count_labels,
                           count_labeled_images=count_labeled_images,
                           count_not_labeled_images=count_not_labeled_images)


@index.route("/output", methods=["GET", "POST"])
@login_required
def output():
    label = request.form.get("label")
    image_id = session.get("curent_image_id", None)
    if label:
        try:
            sql_query_w_commit(create_sql_str_insert_label(
                current_user.username, image_id, label))
            return redirect(url_for("index.main"))
        except BaseException:
            return redirect(url_for("index.main"))
    else:
        return redirect(url_for("index.main"))
