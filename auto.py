from tkinter import TclError
from tkinter.constants import FALSE
from tkinter.ttk import Combobox
import itertools as it
import common


class MyCombobox(Combobox):
    def __init__(self, master=None, allow_other_values=True, additional_validation=None, key_word=None, **kwargs):
        Combobox.__init__(self, master, **kwargs)

        self.m3 = None
        pd = self.tk.call('ttk::combobox::PopdownWindow',
                          self)  # get popdownWindow reference
        lb = pd + '.f.l'  # get popdown listbox
        self.lb = lb
        # self._bind(('bind', self), "<Button-1>", self.showPop, None)
        self._bind(('bind', lb), "<Button-3>", self.delete_item, None)
        self._bind(('bind', lb), "<KeyPress>", self.popup_key_pressed, None)

        self._allow_other_values = allow_other_values
        self.additional_validation = additional_validation
        self.key_word = key_word

        self._validate = self.register(self.validate)
        self.configure(validate='key', validatecommand=(
            self._validate, "%d", "%S", "%i", "%s", "%P"))

    def validate(self, action, modif, pos, prev_txt, new_txt):
        """Complete the text in the entry with values from the combobox."""

        print('action===>', action, modif, pos, prev_txt, new_txt)

        try:
            sel = self.selection_get()
            print('sel===>', sel)
            txt = prev_txt.replace(sel, '')
        except TclError:
            print('TclError===>', )
            txt = prev_txt
        print('txt===>', txt)

        try:
            # 删除
            if action == "0":
                txt = txt[:int(pos)] + txt[int(pos) + 1:]
                if self.additional_validation:
                    self.additional_validation(self, new_txt)
                return True
            else:
                txt = txt[:int(pos)] + modif + txt[int(pos):]
                if self.additional_validation:
                    self.additional_validation(self, new_txt)

                values = self.cget('values')
                
                l = [i for i in values if i[:len(txt)] == txt]
                # print('L===>', l)
                if l:
                    i = values.index(l[0])
                    self.current(i)
                    index = self.index("insert")
                    self.delete(0, "end")
                    self.insert(0, l[0].replace("\ ", " "))
                    self.selection_range(index + 1, "end")
                    self.icursor(index + 1)
                    return True
                else:
                    return self._allow_other_values
        except Exception as e:
            print('Exception e===>', e)
            common.alert(f"{e}")

    def __getitem__(self, key):
        return self.cget(key)

    def config(self, dic={}, **kwargs):
        self.configure(dic={}, **kwargs)

    def configure(self, dic={}, **kwargs):
        dic2 = {}
        dic2.update(dic)
        dic2.update(kwargs)
        self._allow_other_values = dic2.pop(
            'allow_other_values', self._allow_other_values)
        Combobox.config(self, dic2)

    def popup_key_pressed(self, evt):
        values = self.cget("values")

        for i in it.chain(range(self.current() + 1, len(values)), range(0, self.current())):
            if evt.char.lower() == values[i][0].lower():
                self.current(i)
                self.icursor(i)

                # clear current selection
                self.tk.eval(evt.widget + ' selection clear 0 end')

                self.tk.eval(evt.widget + ' selection set ' +
                             str(i))  # select new element

                # spin combobox popdown for selected element will be visible
                self.tk.eval(evt.widget + ' see ' + str(i))

                return

    def delete_item(self, evt):
        values = self.cget("values")

        index = self.tk.getint(self.tk.call(evt.widget, 'nearest', evt.y))

        self.tk.call(evt.widget, 'delete', index, index)

        self.tk.call(evt.widget, 'activate', 0)

        self.tk.call(evt.widget, 'see', index - 1)

        if values[index] in common.config[self.key_word]:
            print('要删除===>', values[index],
                  self.key_word, common.config[self.key_word])
            common.config[self.key_word].remove(values[index])

            history = common.config.get('history', {})
            config = common.config

            if (config['projectName'] in history and values[index] in history[config['projectName']][self.key_word.strip('Tuple')]):
                history[config['projectName']][self.key_word.strip(
                    'Tuple')].remove(values[index])

        v = values[:index] + values[index + 1:]

        self['values'] = v

        self.update()

        return
