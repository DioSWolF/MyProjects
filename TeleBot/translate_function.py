#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from googletrans import Translator
from change_lang_translate import lang_transl, input_lang
from phrases_list import help_bot
from bot_token import bot
from telebot import types


def delete_symbol_in_text(text):
    CLEAN_LIST = "«", "»", "„", "”", "「", "」", "“", "《", "》"

    new_text = ""
    for i in text:
        if i in CLEAN_LIST:
            i = u'"'
        new_text += i

    return new_text


def translate_text(replace_text, lang):
    translator = Translator()
    new_text = []
    word_sek = []
    combi_words = ""
    
    for word in replace_text:

        if (word[0] and word[-1]) == "#":
            if len(combi_words) > 0:
                new_text.append(translator.translate(combi_words, src = input_lang, dest=lang).text)
                combi_words = ""
            new_text.append(word)


        elif word != "||" and word != "|":
            combi_words += " " + word
            if word_sek != []:
                new_text.extend(word_sek)
                word_sek = []

            elif replace_text.index(word) == (len(replace_text) - 1) and (word[0] and word[-1]) != "#":
                word = translator.translate(combi_words, src = input_lang, dest=lang)
                combi_words = translator.translate(combi_words, src = input_lang, dest=lang)
                new_text.append(combi_words.text)

        else: 
            if combi_words != "":
                combi_words = translator.translate(combi_words, src = input_lang, dest=lang)
                new_text.append(combi_words.text)
            new_text.append(word)
            combi_words = ""
    final_text = " ".join(new_text)

    return final_text


def correct_text(text):
    text = text.split()
    sentense_list = []
    text_list = []
    error_elements = [f"ATTENTION! System can not process this element(s) correctly:\n"]
    i = 0
    for word in text:
        word = word.strip()

        if (word != "OR") and (word != "AND") and (word != "NOT") and (word not in re.findall(r"NEAR/\d+", word)):
            sentense_list.append(word)

        else:

            try:
                if (len(sentense_list) > 1) and ((sentense_list[0][sentense_list[0].rfind("(") + 1] != '"') or (sentense_list[0].rfind("(") == -1 and sentense_list[0].find('"') == -1)):
                    find_index = sentense_list[0].rfind('(') + 1
                    sentense_list[0] = f'{sentense_list[0][0:find_index]}"{sentense_list[0][find_index:]}'
            
            except IndexError:
                i += 1
                error_elements.extend(f"{i}) {' '.join(sentense_list)}\n")


            try:
                if (len(sentense_list) > 1) and (sentense_list[-1].find(")") == -1) and (sentense_list[-1].find('"') == -1):
                    find_index = sentense_list[-1].find(")")
                    sentense_list[-1] = f'{sentense_list[-1][0:]}"'

            except IndexError:
                i += 1
                error_elements.extend(f"{' '.join(sentense_list)}\n")
           
            try:
                if (len(sentense_list) > 1) and (sentense_list[-1].find('"') == -1):
                    find_index = sentense_list[-1].find(")")
                    sentense_list[-1] = f'{sentense_list[-1][0:find_index]}"{sentense_list[-1][find_index:]}'
                    text_list.extend(sentense_list)
                    sentense_list = []
                    
            except IndexError:
                i += 1
                error_elements.extend(f"{' '.join(sentense_list)}\n")

            else:
                text_list.extend(sentense_list)
                sentense_list = []

            text_list.append(word)
            text_list.extend(sentense_list)
    del text_list[-1]

    if len(error_elements) > 1:
        text_list.insert(0, f"\n{''.join(error_elements)}\n")
    text_str = " ".join(text_list)

    return text_str


def main(message):
    return_final_text = {}
    if len(message.text) > 3700:
        bot.delete_message(message.chat.id, message.message_id +1)
        bot.send_message(message.chat.id, "Text too long, max 3700 symbols")
        return 
    orig_text = message.text.strip()
    replace_text = orig_text.replace("NOT", "|||").replace("OR", "||").replace("AND", "|")

    near_list = set(re.findall(r"NEAR/\d+", replace_text))
    near_list = list(near_list)
    near_list.sort()
    near_list.sort(key=len, reverse=True)
    for word_near in near_list:
        replace_text = replace_text.replace(word_near, f"#{word_near}#")

    lang_transl.load_data()
    for lang, value_lang in lang_transl[message.chat.id].items():
        replace_text = replace_text.split()
        replace_text.append(" OR #qweasdzxc#")
        transl_text = translate_text(replace_text, lang)
        final_text = transl_text.replace("|||", "NOT").replace("||", "OR").replace("|", "AND").replace("#", "")
        final_text = delete_symbol_in_text(final_text)
        final_text = correct_text(final_text)
        return_final_text[value_lang] = final_text
    return return_final_text

    
def exit_menu(call):
    help_keys, help_text = help_bot(call.message)
    message = call.message
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.edit_message_text(help_text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=help_keys)
    return 


def send_text(call, mess_ind=None):
    if mess_ind != None:
        bot.delete_message(call.chat.id, mess_ind.message_id)
    bot.send_message(call.chat.id, "I need some time to translate it")
    final_text = main(call)
    if final_text != None:
        for lang, trans_text in final_text.items():
            bot.send_message(call.chat.id, f"Language: {lang}\n{trans_text}")
    keyboard = types.InlineKeyboardMarkup()
    key_menu = types.InlineKeyboardButton(text="Back", callback_data="menu")
    keyboard.add(key_menu)  
    mess_ind = bot.send_message(call.chat.id, "Enter text to translate", reply_markup=keyboard)
    return start_translate(call, mess_ind)


def start_translate(call, mess_ind = None):
    bot.register_next_step_handler(call, send_text, mess_ind)
    return


