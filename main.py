import asyncio

from pywebio.pin import *
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js


chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs
    put_markdown("#супер хакерский чат").style('color: #00FF00')

    run_js('''document.body.style.backgroundColor = "#333335";''')
    run_js('''document.getElementById('input-container').style.backgroundColor = "#333335";''')
    run_js('''Array.prototype.slice.call(document.getElementsByTagName('footer')).forEach(function(item) { 
   item.parentNode.removeChild(item); 
} );''')

    img = input('Вставьте ссылку на фото:', type='url')

    imgarr = []

    msg_box = output()

    nickname = await input("Войти", required=True, placeholder="Никнейм", validate=lambda n: "Этот никнейм занят" if n in online_users or n == '' else None)

    online_users.add(nickname)

    chat_msgs.append(('!',f"{nickname} вошёл в чат"))
    msg_box.append(put_markdown(f"{nickname} вошёл в чат").style('color: white'))

    put_scrollable(msg_box, height=500, keep_bottom=True).style('background-color: #000000')

    put_scrollable(put_scope('user_list'), height=200, keep_bottom=True)

    refresh_task = run_async(refresh_msg(nickname, msg_box))


    while True:
        clear(scope='user_list')
        put_text('Пользователи онлайн: ', scope='user_list').style('color:white')
        for user in online_users:
            put_text(user, scope='user_list').style('color: #00FF00')

        data = await input_group("Сообщение", [
            input(placeholder='Текст', name ="msg"),
            actions(name='cmd', buttons=['Отправить', {'label':'Выйти из чата', 'type':'cancel'},'Фото'])
        ], validate=lambda m: ('msg', 'Введите сообщение') if m['cmd'] == 'Отправить' and not m["msg"] else None)

        if data is None:
            break

        if data['cmd'] == 'Фото':
            img = await input('Вставьте ссылку на фото:', type='url')
            if img:
                msg_box.append(put_markdown(f"{nickname} Отправил фото:").style('color: #00FF00'))
                chat_msgs.append((nickname, 'Отправил Фото'))
                chat_msgs.append(img)
                #msg_box.append(put_image(img, width='256px', height='256px'))

        else:
            msg_box.append(put_markdown(f"{nickname}: {data['msg']}").style('color: #00FF00'))
            chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("Вы вышли из чата")
    msg_box.append(put_markdown(f"Пользователь '{nickname}' вышел из чата").style('color: white'))
    chat_msgs.append(('!', f"Пользователь '{nickname}' вышел из чата"))



async def refresh_msg(nickname, msg_box):
    global  chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if len(m)>2:
                msg_box.append(put_image(m, width='256px', height='256px').style('border-radius: 10px'))
            elif isinstance(m[0], str):
                if m[0] != nickname:
                    msg_box.append(put_markdown(f"'{m[0]}': {m[1]}").style('color: white'))

            if len(chat_msgs) > MAX_MESSAGES_COUNT:
                chat_msgs = chat_msgs[len(chat_msgs) // 2:]

            last_idx = len(chat_msgs)

if __name__ == "__main__":
    start_server(main, debug=True, port=8000, cdn=False)