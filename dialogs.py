# coding=utf-8
def dialog_to_multiline_list(dialog):
    """
    Pätkitaan |-merkillä erotetut rivit listan sisälle muotoon:
    [rivi1, rivi2, rivi3, rivi4]
    :param dialog: str
    :rtype: list[str]
    """
    assert isinstance(dialog, str)

    sentence = ""
    dialog_list = ['', '', '', '']
    dialog_line = 0

    for symbol in dialog:
        if symbol == '|':  # Rivi vaihtuu
            dialog_list[dialog_line] = sentence
            dialog_line += 1
            sentence = ''
        else:
            sentence += symbol

    # last line
    dialog_list[dialog_line] = sentence

    return dialog_list


class Dialogs:
    dialogs = {0: 'Null',
               2: 'Test',
               1: 'Hey you!|Welcome to the world of Re:Start',
               }

    def __init__(self):
        pass

    def get_dialog(self, id_int):
        """

        :rtype: [str]
        """
        dialog = dialog_to_multiline_list(self.dialogs[id_int])

        return dialog
