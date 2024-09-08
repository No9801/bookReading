<!doctype html>

<head>
    <title>{{bookTitle}}</title>
    <link rel="stylesheet" type="text/css" href="/static/bookCss.new.css" />
</head>

<body>
    <h1><a href="/"> Back </a></h1>
    <div id="wrapper">
        <div class="box_con">
            <div id="maininfo">
                <div id="info">
                    <h1>{{bookTitle}}</h1>
                </div>
            </div>
        </div>
        <div class="box_con">
            <div id="list">
                <dl>
                    <dt>《{{bookTitle}}》正文</dt>
                    %if version == "old":
                        %for index in range(len(bookContent)):
                        <dd><a href="/content/{{index}}">{{index}} - {{bookContent[index][0]}}</a></dd>
                        %end
                    %elif version == "restruct":
                        %for index, part in enumerate(bookContent):
                        <dd><a href="/content/{{index}}">{{index}} - {{bookContent[index].title}}</a></dd>
                        %end
                    %else:
                        %raise RuntimeError("Version Error: f{version}")
                    %end
                </dl>
            </div>
        </div>
    </div>
</body>

</html>
