import os

from decouple import config


def init_langfuse():
    os.environ["LANGFUSE_SECRET_KEY"] = config("LANGFUSE_SECRET_KEY")
    os.environ["LANGFUSE_PUBLIC_KEY"] = config("LANGFUSE_PUBLIC_KEY")
    os.environ["LANGFUSE_HOST"] = config("LANGFUSE_HOST")
