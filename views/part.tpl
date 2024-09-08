<!doctype html>
<html>

    <head>
        <title>{{partTitle}}</title>
        <link rel="stylesheet" type="text/css" href="/static/bookCss.new.css" />
        <style>
            .block {
                margin-top: 25%;
            }
        </style>
    </head>

    <body>
        <div id="wrapper">
            <div class="content_read">
                <div class="block"></div>
                <div class="box_con">
                    <div class="bookname">
                        <h1>{{partTitle}}</h1>
                        <div class="bottem1">
                            <a href="/content/{{index - 1}}">上一章</a> &larr; 
                            <a href="/index">章节目录</a> &rarr; 
                            <a href="/content/{{index + 1}}">下一章</a>
                        </div>
                    </div>
                    <div id="content">
                        {{!partContent}}
                    </div>
                    <div class="bottem2">
                        <a href="/content/{{index - 1}}">上一章</a> &larr; 
                        <a href="/index">章节目录</a> &rarr; 
                        <a href="/content/{{index + 1}}">下一章</a>
                    </div>
                </div>
                <div class="block"></div>
            </div>
        </div>
    </body>

</html>
