from enum import Enum

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

class LINETemplateMessage(Enum):
    SIMPLE_TEXT = 0
    CONFIRM_TEMPLATE = 1
    FLEX_LINK_BOX = 2

class LINEUtils():

    # テンプレートタイプを複数作れるようにする
    def get_template(self, index, *args, **kwargs):
        if index == LINETemplateMessage.SIMPLE_TEXT:
            if 'text' in kwargs:
                template = TemplateSendMessage(text=kwargs['text'])
                return template
            else:
                template = TemplateSendMessage(text='Sorry.System went wrong.')
                return template
        elif index == LINETemplateMessage.CONFIRM_TEMPLATE:
            confirm_template = ConfirmTemplate(text='Do it?', actions=[
                MessageAction(label='Yes', text='Yes!'),
                MessageAction(label='No', text='No!'),
            ])
            template_message = TemplateSendMessage(alt_text='Confirm alt text', template=confirm_template)
            return template_message
        elif index == LINETemplateMessage.FLEX_LINK_BOX:
            flex_link_template = BubbleContainer(
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text='ほしい記事はこれかな？', weight='bold', size='sm'),
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
                                            text='第1候補',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        ButtonComponent(
                                            style='link',
                                            height='sm',
                                            action=URIAction(label='Google', uri='http://google.com/'),
                                        ),
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='第2候補',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        ButtonComponent(
                                            style='link',
                                            height='sm',
                                            action=URIAction(label='Yahoo', uri='http://yahoo.co.jp/'),
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            )
            template = TemplateSendMessage(alt_text='Confirm alt text', template=flex_link_template)
