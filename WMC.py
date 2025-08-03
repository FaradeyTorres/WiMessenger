import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

# Настройки сети
BROADCAST_PORT = 12345
BROADCAST_ADDR = '255.255.255.255'  # Широковещательный адрес

class WiFiChatApp(App):
    def build(self):
        # Основной макет
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # История сообщений
        self.history_label = Label(
            text='Сообщения появятся здесь...\n', 
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(Window.width - 20, None)
        )
        self.history_label.bind(
            texture_size=self.history_label.setter('size')
        )
        
        scroll = ScrollView()
        scroll.add_widget(self.history_label)
        layout.add_widget(scroll)
        
        # Поле ввода и кнопка
        input_layout = BoxLayout(size_hint_y=0.15)
        self.message_input = TextInput(
            hint_text='Введите сообщение...',
            multiline=False
        )
        send_btn = Button(
            text='ОТПРАВИТЬ',
            size_hint_x=0.3,
            background_color=(0, 0.7, 0, 1),
            on_press=self.send_message
        )
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(send_btn)
        layout.add_widget(input_layout)
        
        # Настройка сокета
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.5)
        self.sock.bind(('', BROADCAST_PORT))
        
        # Запуск потока прослушки
        self.listener_active = True
        self.listener_thread = threading.Thread(target=self.listen_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        return layout

    def send_message(self, instance):
        """ Отправка сообщения """
        message = self.message_input.text.strip()
        if message:
            try:
                self.sock.sendto(
                    message.encode('utf-8'),
                    (BROADCAST_ADDR, BROADCAST_PORT)
                )
                self.message_input.text = ''
                self.update_history(f"Я: {message}")
            except Exception as e:
                self.update_history(f"Ошибка: {str(e)}")

    def listen_messages(self):
        """ Прослушивание сообщений """
        while self.listener_active:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode('utf-8')
                Clock.schedule_once(lambda dt: self.update_history(f"{addr[0]}: {message}"))
            except socket.timeout:
                continue
            except Exception as e:
                pass

    def update_history(self, message):
        """ Обновление истории """
        self.history_label.text += message + '\n'
        # Автопрокрутка вниз
        scroll = self.history_label.parent
        if scroll:
            scroll.scroll_y = 0

    def on_stop(self):
        """ Остановка приложения """
        self.listener_active = False
        self.sock.close()

if __name__ == '__main__':
    WiFiChatApp().run()