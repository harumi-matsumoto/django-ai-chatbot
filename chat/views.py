from __future__ import unicode_literals
from argparse import ArgumentParser
import errno
import os
import sys
import tempfile
import re
import json

from google.appengine.ext import ndb
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)

from .predictor import Predictors


# override LineBotApi
class LineBotApiJSON(LineBotApi):
    def reply_message(self, reply_token, messages, timeout=None, json_flag=None):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]
        if json_flag:
            data = {
                'replyToken': reply_token,
                'messages': messages
            }
        else:
            data = {
                'replyToken': reply_token,
                'messages': [message.as_json_dict() for message in messages]
            }

        self._post(
            '/v2/bot/message/reply', data=json.dumps(data), timeout=timeout
        )

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApiJSON(channel_access_token)

handler = WebhookHandler(channel_secret)

def callback(request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'


def predict(data):
    assert isinstance(request, HttpRequest)
    if request.method == 'GET':
        sentence = request.GET.get('sentence')
        p = Predictor()
        result = p.execute(sentence)
        chat_data.append([sentence,result['Label']])
        return HttpResponse(result['Words'])
    else:
        return HttpResponse("データが不正です")



@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # user = Users.query.filter_by(id = )

    text = event.message.text

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' +
                                    profile.display_name),
                    TextSendMessage(text='Status message: ' +
                                    profile.status_message)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[
            MessageAction(label='Yes', text='Yes!'),
            MessageAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'buttons':
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text',
                               data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'carousel':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackAction(label='ping with text',
                               data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'image_carousel':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='datetime',
                                                            data='datetime_postback',
                                                            mode='datetime')),
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='date',
                                                            data='date_postback',
                                                            mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'imagemap':
        pass
    elif text == 'flex':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(
                                size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(
                                size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(
                                size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(
                                size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(
                                size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(
                            label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == 'quick_reply':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Quick reply',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="label1", data="data1")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="label2", text="text2")
                        ),
                        QuickReplyButton(
                            action=DatetimePickerAction(label="label3",
                                                        data="data3",
                                                        mode="date")
                        ),
                        QuickReplyButton(
                            action=CameraAction(label="label4")
                        ),
                        QuickReplyButton(
                            action=CameraRollAction(label="label5")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="label6")
                        ),
                    ])))
    elif text == "recommend":
        line_bot_api.reply_message(
            event.reply_token, json_data, json_flag=True)
    elif text == "liff":
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text='https://line.me/R/app/1615588360-p4vKyQMV'),
            ]
        )
    elif text == "purchase":
        previous_bot_message = "question"
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=r'商品の購入ですね！\nそれではいくつか質問させてもらいますね。'),
                TextSendMessage(text=r'これから購入のための情報をお聞きしますが、'),
                ConfirmTemplate(
                    action=[
                        MessageAction(
                            label='chat',
                            text='ちゃっとで答える'
                        ),
                        MessageAction(
                            label='webpage',
                            text='Webページで入力する'
                        ),
                    ]
                )
            ]
        )
    elif previous_bot_message == "question" and text == "webpage":
        return redirect("https://26p.jp/ranking", code=302)
    elif previous_bot_message == "question" and text == "chat":
        previous_bot_message = "name"
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=r'ありがとうございます！！'),
                TextSendMessage(text=r'さっそくお名前を教えてもらえますか？'),

            ]
        )
    elif previous_bot_message == "name":
        user.name = text
        user.previous_bot_message = "house_confirm"
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=f'{user.name}さんですね！\nありがとうございます'),
                ConfirmTemplate(text='今はお家ですか?', actions=[
                    URIAction(label='Yes', text='yes', uri=''),
                    URIAction(label='No', text='no', uri=''),
                ])
            ]
        )
    elif previous_bot_message == "house_confirm" and text == "yes":
        user.previous_bot_message = "house"
        line_bot_api.reply_message(
            event.reply_token, [
                TextMessage(address),
                ConfirmTemplate(text='お家の住所はここでよいですか？', actions=[
                    URIAction(label='Yes', text='yes', uri=''),
                    URIAction(label='No', text='no', uri=''),
                ])
            ]
        )
    elif previous_bot_message == "house_confirm" and text == "no":
        user.previous_bot_message = "house"
        line_bot_api.reply_message(
            event.reply_token, [
                TextMessage('お家の住所を入力してください'),
            ]
        )
    elif previous_bot_message == "house":
        user.previous_bot_message = "goods_confirm"
        # クエリでselect_item,municipalities
        # こちらの商品でよろしいですか？
        line_bot_api.reply_message(event.reply_token, goods, json_flag=True)
    elif previous_bot_message == "goods_confirm":
        user.previous_bot_message = "donation_amount"
        # クエリでselect_item,municipalities
        # 寄付金額
        line_bot_api.reply_message(
            event.reply_token, [
                TextMessage('いくら寄付しますか?'),
            ]
        )
    elif previous_bot_message == "donation_amount":
        user.previous_bot_message = "municipalities_used"
        # クエリでselect_item,municipalities
        # 寄付の使い道
        line_bot_api.reply_message(
            event.reply_token, municipalities_used, json_flag=True)
    elif previous_bot_message == "municipalities_used":
        user.previous_bot_message = "donation_info"
        # クエリでselect_item,municipalities
        # 寄付情報の公開(はい、いいえ)
        line_bot_api.reply_message(
            event.reply_token, donation_info, json_flag=True)
    elif previous_bot_message == "donation_info":
        user.previous_bot_message = "municipalities_info"
        # クエリでselect_item,municipalities
        # 自治体(はい、いいえ)
        line_bot_api.reply_message(
            event.reply_token, municipalities_info, json_flag=True)
    elif previous_bot_message == "municipalities_info":
        user.previous_bot_message = "support_message"
        # クエリでselect_item,municipalities
        # 応援メッセージがあればお願いします。
        line_bot_api.reply_message(
            event.reply_token, support_message, json_flag=True)
    elif previous_bot_message == "support_message":
        user.previous_bot_message = "onestop_payment"
        # クエリでselect_item,municipalities
        # ワンストップ特例を希望するかどうか
        line_bot_api.reply_message(
            event.reply_token, onestop_payment, json_flag=True)
    elif previous_bot_message == "onestop_payment":
        user.previous_bot_message = "info_confirm"
        # クエリでselect_item,municipalities
        # 情報確認
        line_bot_api.reply_message(
            event.reply_token, info_confirm, json_flag=True)
    elif previous_bot_message == "info_confirm" and text == "yes":
        user.previous_bot_message = "payment"
        # クエリでselect_item,municipalities
        # 支払いを行う
        line_bot_api.reply_message(event.reply_token, payment, json_flag=True)
    elif previous_bot_message == "info_confirm" and text == "no":
        user.previous_bot_message = "fix"
        # クエリでselect_item,municipalities
        # 何を修正しますか？
        line_bot_api.reply_message(event.reply_token, fix, json_flag=True)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url +
                            os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url +
                            os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(FollowEvent)
def handle_follow(event):
    new_user = Users()
    new_user.line_id = event.source.user.user_id
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))


@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))

# ユーザデータの取得
def get_line_user():
    user_data = line_bot_api.get_profile(event.source.user_id)
    user = Users().query(line_id=user_data[''])
    return user


# DBの値を修正
def sql(data):
    # lineidからDBの情報を確認してDataを返す
    return True