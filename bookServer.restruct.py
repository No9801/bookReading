import argparse
import bottle
import dataclasses
import json
import os
from pathlib import Path
import re
import sys
from typing import Optional, TypedDict


SPLIT_CHAR = "\uabcd"


@dataclasses.dataclass(frozen=True)
class Config:
    bookFile: str
    bookTitle: Optional[str] = None
    partRe: Optional[str] = None
    bookCode: str = "utf-8"
    serverHost: str = "127.0.0.1"
    serverPort: int = 8080


@dataclasses.dataclass(frozen=True)
class Chapter:
    title: str
    content: str


def getConfig(configFile: str, configEncoding: str) -> Config:
    with open(configFile, "r", encoding=configEncoding) as f:
        configDict = json.load(f)
    return Config(**configDict)


def getPart(content: str, pattern: re.Pattern) -> Chapter:
    contentList = (pattern
        .sub(f"\\1{SPLIT_CHAR}", content)
        .split(SPLIT_CHAR))
    if len(contentList) == 1:
        return Chapter("Unknown", contentList[0])
    elif len(contentList) == 2:
        return Chapter(*contentList)
    raise RuntimeError(f"Wrong element counts: {len(contentList)} in function getPart")


def getParts(content: str, config: Config) -> list[Chapter]:
    if config.partRe is None:
        bookName = Path(config.bookFile).stem
        return [Chapter(bookName, content)]
    pattern = re.compile(f"({config.partRe})")
    contentList = (pattern
        .sub(f"{SPLIT_CHAR}\\1", content)
        .split(SPLIT_CHAR))
    return list(
        map(lambda chapter: getPart(chapter, pattern),
            contentList))


def access(port: int) -> bool:
    """
    To test if the port can use
    :param `port`: The port of computer \\
    Return `True` if the port can use else `False`
    """
    if port < 1024 or 65535 < port:
        # privileged port
        # out of range
        return False

    if "win32" == sys.platform:
        cmd = 'netstat -aon|findstr ":%s "' % port
    elif "linux" == sys.platform:
        cmd = 'netstat -aon|grep ":%s "' % port
    else:
        print("Unsupported system type %s" % sys.platform)
        return False

    with os.popen(cmd, "r") as f:
        if "" != f.read():
            print("Port %s is occupied" % port)
            return False
        else:
            return True


def runServer(parts: list[Chapter], config: Config) -> None:
    app = bottle.Bottle()

    class IndexViewDict(TypedDict):
        bookTitle: str
        bookContent: list[Chapter]
        version: str

    class ContentViewDict(TypedDict):
        partTitle: str
        partContent: str
        index: int

    @app.get("/index")  # type: ignore
    @app.get("/")  # type: ignore
    @bottle.view("index")
    def getIndex() -> IndexViewDict:
        return {
            "bookTitle": (
                config.bookTitle if config.bookTitle is not None else "Unknown"
            ),
            "bookContent": parts,
            "version": "restruct",
        }

    @app.get("/json/index")  # type: ignore
    @app.get("/json")  # type: ignore
    def getIndexJson() -> IndexViewDict:
        return {
            "bookTitle": (
                config.bookTitle if config.bookTitle is not None else "Unknown"
            ),
            "bookContent": [
                {
                    "content": f"{part.content[:100]}...",
                    "title": part.title,
                    "url": f"/content/{index}",
                }
                for index, part in enumerate(parts)
            ],
            "version": "restruct",
        }

    @app.get("/content/<index:int>")  # type: ignore
    @bottle.view("part")
    def getPart(index: int) -> ContentViewDict:
        index %= len(parts)
        content = (parts[index].content
            .replace(" ", "&nbsp;")
            .replace("\n", "<br />"))
        return {"partTitle": parts[index].title, "partContent": content, "index": index}

    @app.get("/json/content/<index:int>")  # type: ignore
    def getPartJson(index: int) -> ContentViewDict:
        index %= len(parts)
        content = (parts[index].content
            .replace(" ", "&nbsp;")
            .replace("\n", "<br />"))
        return {"partTitle": parts[index].title, "partContent": content, "index": index}

    @app.get("/static/<filename:path>")  # type: ignore
    def getStatic(filename: str):
        return bottle.static_file(filename, root="E:/bookReading/static")

    serverPort = config.serverPort
    # while not access(serverPort):
    #     serverPort += 1

    bottle.run(
        app,
        host=config.serverHost,
        port=serverPort,
        server="tornado",
        debug=True,
        reloader=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="BookReading", description="A program which hold a server"
    )
    parser.add_argument("--config", "-c", type=str, required=True)
    parser.add_argument(
        "--config-encoding", "-e", type=str, required=False, default="utf-8"
    )
    args = parser.parse_args()

    config = getConfig(args.config, args.config_encoding)
    with open(config.bookFile, "r", encoding=config.bookCode) as book:
        parts = getParts(book.read(), config)
    runServer(parts, config)


if __name__ == "__main__":
    main()
