import os
from flask import Flask, jsonify

app = Flask(__name__)

import StringIO
import requests
from lxml import etree


def get_from_hn():
    headers = {"User-agent": "Mozilla/5.0", "Cookie": "__is_access=YES"}
    url = "http://news.ycombinator.com"
    res = requests.get(url, headers=headers, timeout=30)
    data = res.text
    data = data.lstrip()
    parser = etree.HTMLParser(encoding='UTF-8', strip_cdata=False)
    root = etree.parse(StringIO.StringIO(data), parser).getroot()
    root
    titles = root.xpath("""//td[@class="title"]/a/text()""")
    titles = titles[:len(titles) - 1]
    urls = root.xpath("""//td[@class="title"]/a/@href""")
    urls = urls[:len(urls) - 1]
    points = [x.split('points')[0].strip() for x in root.xpath("""//td[@class="subtext"]/span[1]/text()""")]
    num_comments = [x.split('comment')[0].strip() for x in root.xpath("""//td[@class="subtext"]/a[2]/text()""")]
    num_comments = [x if x != "discuss" else "0" for x in num_comments]
    comment_urls = ["http://news.ycombinator.com/{}".format(x) for x in root.xpath("""//td[@class="subtext"]/a[2]/@href""")]
    return {
        "titles": titles,
        "urls": urls,
        "points": points,
        "num_comments": num_comments,
        "comment_urls": comment_urls,
    }


@app.route('/')
def json_api():
    info_dict = get_from_hn()
    titles = info_dict['titles']
    urls = info_dict['urls']
    points = info_dict['points']
    num_comments = info_dict["num_comments"]
    comment_urls = info_dict["comment_urls"]
    total_list = (titles, urls, points, num_comments, comment_urls)
    items = [
        {
            "title": total_list[0][i],
            "url": total_list[1][i],
            "points": total_list[2][i],
            "commentCount": total_list[3][i],
            "commentUrl": total_list[4][i],
        }
        for i in range(len(titles))]
    json_data = {'items': items}

    return jsonify(**json_data)




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
