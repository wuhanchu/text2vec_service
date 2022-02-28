import os


class Config:
    """
    配置信息
    """

    AUTO_TOKEN = False
    MODEL = os.getenv("MODEL", "paraphrase-multilingual-mpnet-base-v2")  # 调用的模型
    MODELS_PATH = os.getenv("MODELS_PATH", "./models")  # 模型位置

    MODEL_PATH = os.path.join(MODELS_PATH, MODEL)

    TOKEN_PATH = os.getenv("TOKEN_PATH", "./models/token.txt")  # 词汇文件
    TOKEN_URL = os.getenv(
        "TOKEN_URL",
        "http://101.231.133.233:31016/z_know_info/api/domain/token",
    )  # 词汇文件的接口返回
