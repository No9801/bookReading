import sys

sigquote = "'"

with open(f"{sys.argv[4]}.json", "w", encoding="utf-8") as f:
    f.write(f"""{{
    "bookTitle": "{sys.argv[1]}",
    "bookFile": "{repr(sys.argv[2]).strip(sigquote)}",
    "partRe": "第.*?章 .*?\\n",
    "serverPort": {sys.argv[3]}
}}""")

