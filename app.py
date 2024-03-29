import os

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    TextSendMessage # text message
    )

import pya3rt # CURL

app = Flask(__name__)

# Line messange api
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Talk api
TALKAPI_KEY = os.environ["TALKAPI_KEY"]
client = pya3rt.TalkClient(TALKAPI_KEY)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def response_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return

    # notesのCarouselColumnの各値は、変更してもらって結構です。
#    notes = [CarouselColumn(thumbnail_image_url="https://renttle.jp/static/img/renttle02.jpg",
#                            title="【ReleaseNote】トークルームを実装しました。",
#                            text="creation(創作中・考え中の何かしらのモノ・コト)に関して、意見を聞けるようにトークルーム機能を追加しました。",
#                            actions=[{"type": "message","label": "サイトURL","text": "https://renttle.jp/notes/kota/7"}]),
#
#             CarouselColumn(thumbnail_image_url="https://renttle.jp/static/img/renttle03.jpg",
#                            title="ReleaseNote】創作中の活動を報告する機能を追加しました。",
#                            text="創作中や考え中の時点の活動を共有できる機能を追加しました。",
#                            actions=[
#                                {"type": "message", "label": "サイトURL", "text": "https://renttle.jp/notes/kota/6"}]),
#
#             CarouselColumn(thumbnail_image_url="https://renttle.jp/static/img/renttle04.jpg",
#                            title="【ReleaseNote】タグ機能を追加しました。",
#                            text="「イベントを作成」「記事を投稿」「本を登録」にタグ機能を追加しました。",
#                            actions=[
#                                {"type": "message", "label": "サイトURL", "text": "https://renttle.jp/notes/kota/5"}])]

    response = client.talk(event.message.text)

    messages = TextSendMessage()
    if response["status"] == 0:
        text = ""
        for result in response["results"]:
            #text.append(result["reply"])
            text += result["reply"]
    
        messages = TextSendMessage(
            text=text
        )

    else:
        messages = TextSendMessage(
            text="何言ってるか理解できないにゃ！" + "Please contact to developer."
        )

    line_bot_api.reply_message(event.reply_token, messages=messages)

    profile = line_bot_api.get_profile(event.source.user_id)

    messages = TextSendMessage(
        text="Text from: " + profile.display_name + ", userId: " + profile.user_id + ", pic: " + profile.picture_url + ". message: " + event.message.text
    )

    to = 'U3bb522904f837fba8b3d6bbceae8849a'
    line_bot_api.push_message(to, messages)



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
