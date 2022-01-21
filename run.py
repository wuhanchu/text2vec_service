# -*- coding: utf-8 -*-

"""
Documents: https://github.com/shibing624/text2vec
"""
import os

import requests
from flask import request, jsonify, Flask
from flask_apscheduler import APScheduler
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim, semantic_search

from config import Config

app = Flask(__name__, root_path=os.getcwd())

personal_model_path = "./models/personalized"  # 个性化模型路径
scheduler = APScheduler()


# 加载已有分词
if os.path.exists(personal_model_path):
    model = SentenceTransformer(personal_model_path)
else:
    model = SentenceTransformer(Config.MODEL_PATH)


@app.route("/token/sync", methods=["POST"])
def post_token_load():
    """
    同步定义的分词信息
    :return:
    """
    token_load()

    return jsonify({"result": True})


@app.route("/token/upload", methods=["POST"])
def post_token_upload():
    """
    同步定义的分词信息
    :return:
    """
    extentd_token = request.json().get("token")
    token_load(extentd_token, False)

    return jsonify({"result": True})


@app.route("/tokenize", methods=["POST"])
def tokenize():
    """
    计算句子与文档集之间的相似度值
    :return:
    """
    global model

    param = {**(request.form or {}), **(request.json or {})}
    sentences = param.pop("sentences")
    return jsonify({"result": model.tokenizer.tokenize(sentences)})


@app.route("/semantic_search", methods=["POST"])
def paraphrase_semantic_search():
    """
    计算句子与文档集之间的相似度值
    :return:
    """
    global model

    param = {**(request.form or {}), **(request.json or {})}
    sentences1 = param.pop("sentences1")
    sentences2 = param.pop("sentences2")
    embeddings1 = model.encode(sentences1)
    embeddings2 = model.encode(sentences2)
    hits = semantic_search(embeddings1, embeddings2, **param)

    return jsonify({"result": hits})


@app.route("/cos_sim", methods=["POST"])
def paraphrase_cos_sim():
    """
    计算句子之间的相似度值
    :return:
    """
    param = {**(request.form or {}), **(request.json or {})}
    sentences1 = param.pop("sentences1")
    sentences2 = param.pop("sentences2")
    embeddings1 = model.encode(sentences1)
    embeddings2 = model.encode(sentences2)
    cosine_scores = cos_sim(embeddings1, embeddings2)

    return jsonify({"result": cosine_scores.tolist()})


@app.route("/computing_embeddings", methods=["POST"])
def computing_embeddings():
    """
    计算句向量
    :return:
    """
    param = {**(request.form or {}), **(request.json or {})}
    sentences = param.pop("sentences")
    embeddings = model.encode(sentences)

    return jsonify({"result": embeddings.tolist()})


def token_load(extend_token=[], load_from_token_url=True):
    """
    加载个性化词汇重新训练模型

    Args:
        extend_token (list, optional): 外部自定义词汇. Defaults to [].
        load_from_token_url (bool, optional): 是否从远程地址进行获取词汇数据. Defaults to True.
    """
    global model

    tokens = []
    model = SentenceTransformer(Config.MODEL_PATH)

    # 加载分词
    if Config.TOKEN_PATH and os.path.exists(Config.TOKEN_PATH):
        with open(Config.TOKEN_PATH, "r") as file:
            data = file.read().split("\n")
            tokens.extend(data or [])

    # 从远程词库获取数据
    if Config.TOKEN_URL:
        response = requests.get(Config.TOKEN_URL)

        if response.ok:
            content = response.json()
            tokens.extend(content.get("data") or [])
        else:
            print("error load token from url")

    # 继承扩展词汇
    tokens.extend(extend_token)

    # 根据大小词汇进行排序
    tokens = sorted(set(tokens), key=lambda item: len(item), reverse=True)
    model.tokenizer.add_tokens(tokens, special_tokens=True)
    model._first_module().auto_model.resize_token_embeddings(len(model.tokenizer))
    model.save(personal_model_path)
    model = SentenceTransformer(personal_model_path)

    print("success load token")


@scheduler.task("interval", id="do_job_1", seconds=1)
def job():
    print("schedule is work")


@scheduler.task("cron", id="auto_job_1", day="*", hour="0", minute="0", second="0")
def auto_token_load():
    if Config.AUTO_TOKEN:
        token_load()


# 运行
if __name__ == "__main__":
    scheduler.init_app(app)
    scheduler.start()
    app.run("0.0.0.0", port=5000)
