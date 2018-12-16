import os

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

from encryption import Encryption

# Main encrypting class for file signing
encrypt = Encryption()


class ScreenManagement(ScreenManager):
    """
    Class for managing different windows
    """
    pass


class Windows(GridLayout):
    """
    SuperClass for all windows.
    It includes handling fonts,
    opening and saving file, converting to rgb
    """
    input_file_name = ''
    are_keys_set = False

    def __init__(self, *args, **kwargs):
        self.dark_color = self.convert_to_rgb(55)
        self.dark_color_lighter = self.convert_to_rgb(67)
        self.light_color = self.convert_to_rgb(244)
        self.red_color = self.convert_to_rgb(*[251, 54, 64])
        self.blue_color = self.convert_to_rgb(*[197, 235, 195])
        self.blue_color_darker = self.convert_to_rgb(*[0, 16, 99])
        super().__init__(**kwargs)

    @staticmethod
    def regular_font(text):
        """
        Converting button to regular open sans font
        :param text:
        :return:
        """
        return f'[font=OpenSans-Regular]{text}[/font]'

    @staticmethod
    def convert_to_rgb(*args):
        """
        Converting int to rgb
        :param args: list of r, g, b
        :return: kivy representation of rgb
        """

        def _convert_to_kivy(color):
            return color / 255

        rgb = []
        if len(args) == 1:
            for _ in range(3):
                rgb.append(_convert_to_kivy(args[0]))
        elif len(args) == 3:
            for color in range(3):
                rgb.append(_convert_to_kivy(args[color]))
        rgb.append(1)
        return tuple(rgb)

    def dismiss_popup(self):
        """
        Closing popup window
        :return: None
        """
        self._popup.dismiss()

    def show_load(self):
        """
        Showing load file dialog
        :return: none
        """
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        """
        Showing saving file dialog
        :return: None
        """
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        """
        Load file handling
        :param path: path to file
        :param filename: full path to file
        :return: none
        """
        self.input_file_name = filename[0]
        self.dismiss_popup()

    def save(self, path, filename):
        """
        Saving file handling
        :param path: path to file
        :param filename: saving full path to file
        :return: None
        """
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()


class MainWindow(Windows, Screen):
    """
    Main window, that includes file signing functions
    """
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    _create_signature = BooleanProperty(True)
    _check_signature = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        self.input_file_name = ''
        super().__init__(*args, **kwargs)

    def on_enter(self):
        Clock.schedule_once(self.update_label)

    def update_label(self, value):
        """
        Updating labels after opening main window
        :param value: unused, but need to be transfered
        :return: none
        """
        self.ids.file_status_label.text = '[font=OpenSans-Light]File status: [/font]'
        self.ids.file_status_label.text = self.ids.file_status_label.text + '[font=OpenSans-Regular]File is not opened.[/font]' if not Windows.input_file_name \
            else f'[font=OpenSans-Regular]Opened file: {Windows.input_file_name.split("/")[-1]}[/font]'

        self.ids.opened_status_label.text = "[font=OpenSans-Light]Key status: [/font][font=OpenSans-Regular]Keys are not set! \nPlease, set up keys in [font=OpenSans-Bold]key settings[/font] menu[/font]" if not Windows.are_keys_set \
            else "[font=OpenSans-Light]Key status: [/font][font=OpenSans-Regular]Keys are set successfully.[/font]"
        if encrypt.keys.get('n'):
            self.ids.n_key_input.text = str(encrypt.keys['n'])
            self.ids.n_key_check.text = str(encrypt.keys['n'])

        if encrypt.keys.get('e'):
            self.ids.public_key_check.text = str(encrypt.keys['e'])

    @property
    def create_signature(self):
        return self._create_signature

    @create_signature.setter
    def create_signature(self, value):
        self._create_signature = value
        self._check_signature = not value

    @property
    def check_signature(self):
        return self._check_signature

    @check_signature.setter
    def check_signature(self, value):
        self._check_signature = value
        self._create_signature = not value

    def load(self, path, filename):
        """
        Load file handling
        :param path: path to file
        :param filename: full path to file
        :return: none
        """
        Windows.input_file_name = filename[0]
        self.dismiss_popup()
        self.update_label(1)

    def sign_file(self, signature_input):
        """
        Creating file digital signature
        :param signature_input: signature input text field
        :return: none
        """
        if Windows.are_keys_set and Windows.input_file_name:
            try:
                signature = encrypt.get_signature_private(Windows.input_file_name)
                signature_input.text = str(signature)
            except KeyError:
                content = ErrorDialog(message="Keys error", close=self.dismiss_popup)
                self._popup = Popup(title="Key saving", content=content,
                                    size_hint=(0.9, 0.9))
                self._popup.open()
        else:
            content = ErrorDialog(message="Signing error", close=self.dismiss_popup)
            self._popup = Popup(title="Key saving", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()

    def is_signature_valid(self, _signature, _public_key, _n_key):
        """
        Handling 'Check signature' button. Checking if file signature is valid
        :param _signature: signature text field
        :param _public_key: public key text field
        :param _n_key: n key text field
        :return: None
        """
        try:
            signature = int(_signature.text)
            e_key = int(_public_key.text)
            n_key = int(_n_key.text)
            public_key = {'e': e_key, 'n': n_key}
        except Exception:
            self.ids.is_valid_signature_label.text = ''
            content = ErrorDialog(message="Keys are not valid", close=self.dismiss_popup)
            self._popup = Popup(title="Key checking", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
            return

        validation = encrypt.is_signature_valid(Windows.input_file_name, signature, public_key)
        self.ids.check_file_hash.text = str(validation[1])
        self.ids.check_file_hash_recovered.text = str(validation[2])
        if validation[0]:
            self.ids.is_valid_signature_label.text = '[font=OpenSans-Bold]Signature is valid[/font]'
        else:
            self.ids.is_valid_signature_label.text = '[font=OpenSans-Bold]Signature is invalid[/font]'


class SettingKeys(Windows, Screen):
    """
    Class of handling settings windows
    """

    def save_keys(self, p_value, q_value, e_value, d_value):
        """
        Saving key button. It handles all fields in setting and filling it
        automately. If fields are filled not correctly, it raises error
        :param p_value: p field
        :param q_value: q field
        :param e_value: e (public key) field
        :param d_value: d (private key) field
        :return: None
        """
        try:
            if not p_value.text:
                encrypt.keys['p'] = self.generate_random_key(p_value, 'p')
            else:
                encrypt.keys['p'] = int(p_value.text)
            if not q_value.text:
                encrypt.keys['q'] = self.generate_random_key(q_value, 'q')
            else:
                encrypt.keys['q'] = int(q_value.text)
            if not e_value.text:
                encrypt.keys['e'] = self.generate_private_public_key(e_value, 'e')
            else:
                encrypt.keys['e'] = int(e_value.text)
            if not d_value.text:
                encrypt.keys['d'] = self.generate_private_public_key(d_value, 'd')
            else:
                encrypt.keys['d'] = int(d_value.text)

            keys = encrypt.set_keys(**encrypt.keys)
            if encrypt.check_keys(keys):
                Windows.are_keys_set = True
                content = ErrorDialog(message="Saved successful.", close=self.dismiss_popup)
                self._popup = Popup(title="Key saving", content=content,
                                    size_hint=(0.9, 0.9))
                self._popup.open()
            else:
                raise Exception
        except Exception:
            Windows.are_keys_set = False
            content = ErrorDialog(message="Filling error", close=self.dismiss_popup)
            self._popup = Popup(title="Key saving", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()

    @staticmethod
    def generate_random_key(key, value):
        """
        Generates p or q key
        :param key: p or q field
        :param value: string 'p' or 'q'
        :return: int value of key
        """
        key_result = encrypt.generate_key(value)
        key.text = str(key_result)
        return int(key.text)

    def generate_private_public_key(self, text_area, key):
        """
        Generating public or private key depends on field to fill
        :param text_area: 'e' of 'd' field in settings
        :param key: string 'e' (public key) or 'd' (private key)
        :return: int value of key
        """
        try:
            keys = encrypt.generate_keys(_public_key=int(self.ids.e_value.text if self.ids.e_value.text else '0'),
                                         _private_key=int(self.ids.d_value.text if self.ids.d_value.text else '0'))
            text_area.text = str(keys[key])
            return int(text_area.text)
        except KeyError:
            content = ErrorDialog(message="P and Q keys error", close=self.dismiss_popup)
            self._popup = Popup(title="Key generating", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()


class LoadDialog(FloatLayout):
    """
    Class for loading new file to convert
    """
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    """
    Class for saving signed file
    """
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ErrorDialog(FloatLayout):
    """
    Message box for showing errors
    """
    message = ObjectProperty(None)
    close = ObjectProperty(None)


presentation = Builder.load_file("rsasignature.kv")


class RSASignatureApp(App):
    """
    Main app, that runs everything
    """
    title = "RSA digital signature"

    def build(self):
        return presentation


Factory.register('MainWindow', cls=MainWindow)
Factory.register('SettingKeys', cls=SettingKeys)
Factory.register('ErrorDialog', cls=ErrorDialog)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == "__main__":
    RSASignatureApp().run()
