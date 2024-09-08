# -- coding=utf-8 --
"""
A program which start a server to read books.
Usage: python bookServer.py --config ConfigFile [--cEncoding configEncoding]

:author: Reisende von Venti
:time: 2023/04/08
"""

# 读取配置
# 给小说分段、分节
# 储存在列表里
# 用bottle展示成网页的形式

import os
import sys
import re
from typing import Optional
import bottle
import json  # 读取json格式的配置
import yaml  # 读取yaml格式的配置
from pathlib import Path

import argparse


# import asyncio


class Config:
    def __init__(self, **otherConfig):
        self.otherConfig = otherConfig

    def __getattr__(self, attrName: str):
        return self.otherConfig.get(attrName, None)


class SimpleConfig(Config):
    def __init__(
            self, bookFile: str,
            bookTitle: Optional[str] = None,
            partRe: Optional[str] = None,
            bookCode: str = "utf-8",
            serverHost: str = "127.0.0.1",
            serverPort: int = 8080,
            **otherConfig
    ):
        self.bookTitle = bookTitle if bookTitle else (
            Path(bookFile).stem if bookFile else "Undefined"
        )
        self.bookFile = bookFile
        self.partRe = partRe
        self.bookCode = bookCode
        self.serverHost = serverHost
        self.serverPort = serverPort
        super().__init__(**otherConfig)

    
        
class DirConfig(Config):
    def __init__(self, dir: str, partRe: str, **otherConfig):
        self.dir = dir
        self.partRe = partRe
        super().__init__(**otherConfig)


class BaseContent:
    pass


class Content(BaseContent):
    def __init__(self, config: SimpleConfig):
        with open(config.bookFile, "r", encoding=config.bookCode) as f:
            content = f.read()
        contentTuple = getParts(content, config)

        self.app = bottle.Bottle()

        @self.app.get("/index")  # type: ignore
        @self.app.get("/")  # type: ignore
        @bottle.view("index")
        def getIndex():
            return {
                "bookTitle": config.bookTitle,
                "bookContent": contentTuple,
                "version": "old"
            }

        @self.app.get("/content/<index:int>")  # type: ignore
        @bottle.view("part")
        def getPart(index: int):
            index = index % len(contentTuple)
            content = contentTuple[index][1].replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;").replace("\n", "<br />")
            return {
                "partTitle": contentTuple[index][0],
                "partContent": content,
                "index": index
            }

        @self.app.get("/static/<filename:path>")  # type: ignore
        def getStatic(filename):
            return bottle.static_file(filename, root="E:/bookReading/static")

class DirContent(BaseContent):
    def __init__(self, config: DirConfig):
        self.files = next(os.walk(config.dir))[-1]
        self.fileDir = {hash(file): file for file in self.files}

        self.app = bottle.Bottle()
        #TODO



# def _getEncoding(filename: str, parser: Callable[[TextIO], dict]) -> str:
#     encoding: str = "utf-8"
#     with open(filename, mode="r", encoding="latin-1") as _f:
#         _d: dict = parser(_f)
#         _e: str = _d.get("encoding", None)
#         if _e is not None:
#             encoding = _e
#     return encoding


def readConfig(filename: str, encoding: str) -> dict:
    # with open(filename, "r", encoding=_getEncoding(filename, json.load)) as f:
    with open(filename, "r", encoding=encoding) as f:
        configDict = json.load(f)
    return configDict


def readYamlConfig(filename: str, encoding: str) -> dict:
    # with open(filename, "r", encoding=_getEncoding(filename, lambda x: yaml.load(x, Loader=yaml.FullLoader))) as f:
    with open(filename, "r", encoding=encoding) as f:
        configDict = yaml.load(f, Loader=yaml.FullLoader)
    return configDict


def _getPart(content: str, regex: re.Pattern) -> tuple[str, str]:
    content = regex.sub("\\1\uabcd", content)
    contentList = content.split("\uabcd")
    contentLength = len(contentList)
    if contentLength == 1:
        contentList = ["Unknown"] + contentList
    elif contentLength == 2:
        pass
    else:
        raise ValueError(f"Too much element: {contentLength} in function _getPart")
    return tuple(contentList) # type: ignore


def getParts(content: str, config: Config) -> tuple[tuple[str, str]]:
    """
    :return:
    ```
    (
        (
            firstPartTitle,
            firstPartContent
        ),
        (
            secondPartTitle,
            secondPartContent
        ),
        ...
    )
    ```
    """
    if config.partRe is None:
        bookName = Path(config.bookFile).stem
        return (bookName, content),
    partRe = re.compile(f"({config.partRe})")
    content = partRe.sub("\uabcd\\1", content)
    contentList = content.split("\uabcd")
    return tuple(map(lambda x: _getPart(x, partRe), contentList)) # type: ignore


def access(port: int) -> bool:
    """To test if the port can use
    :param port: The port of computer
    :type port: int
    :return: `True` if the port can use else `False`
    :rtype: bool
    """
    if port < 1024 or 65535 < port:
        # privileged port
        # out of range
        return False

    if 'win32' == sys.platform:
        cmd = 'netstat -aon|findstr ":%s "' % port
    elif 'linux' == sys.platform:
        cmd = 'netstat -aon|grep ":%s "' % port
    else:
        print('Unsupported system type %s' % sys.platform)
        return False

    with os.popen(cmd, 'r') as f:
        if '' != f.read():
            print('Port %s is occupied' % port)
            return False
        else:
            return True

def get_config(filename: str, encoding: str, suffix: str, configType: type[Config]) -> Config:
    if suffix == ".json":
        config = configType(**readConfig(filename, encoding))
    elif suffix == ".yaml":
        config = configType(**readYamlConfig(filename, encoding))
    else:
        raise NotImplementedError("Config must be .json or .yaml file!")
    return config



def main():
    parser = argparse.ArgumentParser(prog="BookReading", description="A program which hold a server")
    parser.add_argument("--config", "-c", type=str, required=True)
    parser.add_argument("--config-encoding", "-e", type=str, required=False, default="utf-8")
    # parser.add_argument("--bEncoding", "-b", type=str, required=False, default="utf-8")
    args = parser.parse_args()
    file = Path(args.config)
    suffixes = file.suffixes
    if len(suffixes) == 1:
        config = get_config(args.config, args.config_encoding, suffixes[-1], SimpleConfig)
        content = Content(config) # type: ignore
    
    serverPort = config.serverPort
    serverHost = config.serverHost

    while not access(serverPort):
        serverPort += 1

    

    bottle.run(
        content.app,
        host=serverHost,
        port=serverPort,
        server="tornado",
        debug=True,
    )


if __name__ == "__main__":
    main()
