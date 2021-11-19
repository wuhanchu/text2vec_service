import os


class Config:
    """
    配置信息
    """

    MODEL = os.getenv("MODEL", "paraphrase-multilingual-MiniLM-L12-v2")  # 调用的模型
    MODELS_PATH = os.getenv("MODELS_PATH", "./models")  # 模型位置

    MODEL_PATH = os.path.join(MODELS_PATH, MODEL)

    TOKEN_PATH = os.getenv("MODEL", "./token.txt")  # 词汇文件
    TOKEN_URL = os.getenv("MODEL")  # 词汇文件的接口返回
