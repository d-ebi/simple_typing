# -*- coding: utf-8 -*-

# built-in
import datetime
import json
import os
import random
import re
import sys

# pip
from pynput import keyboard
from pynput.keyboard import Key, Listener

class SimpleTyping:
    '''====
    概要
    ====

    | コマンドラインで簡単にタイピングの練習ができるツール.
    | 使用するにはpipでpynputを入れておく必要がある.

    ::
        $ pip install pynput

    動作OS
    ======

        * Windows
        * Linux(X Windowがインストールされていること)

    Pythonのバージョン
    ==================

        Python 3.4以上

    起動例
    ======

    引数にはsymbol,number,alphabetの組み合わせを設定できる.

    ::
        $ python simple_typing symbol,number

    '''

    CHARS = '''1234567890-=\`[];',./qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+|~{}:"<>?QWERTYUIOPASDFGHJKLZXCVBNM'''
    DATA_DIR = './datas'
    SHIFT_KEYS = {keyboard.Key.shift, keyboard.Key.shift_r}

    def __init__(self, targets):
        '''| インスタンスを作成する.
        | プログラムを開始するための変数準備,ディレクトリ準備を行なう.
        | 引数であるtargetsに従ってSimpleTyping.CHARSの中から文字列を抽出し,
        | 並び順をランダムにしたうえでself.random_charsに格納している.

        Attributes:
            :random_chars str     : ランダマイズされた文字列を格納する.
            :current      set     : shiftが押されているかどうかを格納する.
            :records      list    : 正しくタイプされたか,タイプされるまで何秒かかったかなどの情報を格納する.
            :start_time   datetime: タイプすべきキーがコンソールに表示されたときの時刻を格納する.
            :end_time     datetime: タイプされたあとの時刻を格納する.

        Args:
            :targets list: 対象の文字種を指定する.symbol・number・alphabetを組み合わせて指定できる.
        '''

        self.random_chars = str()
        self.current = set()

        self.records = list()

        self.start_time = str()
        self.end_time = str()

        os.makedirs(SimpleTyping.DATA_DIR, exist_ok=True)
        extracted_chars = self.extract_chars(targets)
        indexes = self.get_random_indexes(extracted_chars)
        self.random_chars = self.sort_chars_from_indexes(extracted_chars, indexes)

    def display_target_key(self, result=None):
        '''| コンソール上にタイプすべき対象のキーを表示する.
        | また,前回入力が成功だったか否かも表示している.
        | 引数resultを省略すると初回表示用の出力を行なう.
        | ここで画面表示を行なった後,self.start_timeに値を格納する.

        Args:
            :result str: 前回の表示結果
        '''

        print(result if result else 'Start!')
        print('Key: {}'.format(self.random_chars[0]))
        self.start_time = datetime.datetime.now()

    def extract_chars(self, targets):
        '''引数に指定された種別の文字列のみを返却する.

        Args:
            :targets list: 抜き出す文字列種別のlist(symbol, number, alphabet)
        Returns:
            :str: 指定された文字列

        >>> st = SimpleTyping()
        >>> st.extract_chars(['symbol'])
        '-=\\\\`[];\\',./!@#$%^&*()_+|~{}:"<>?'
        >>> st.extract_chars(['number'])
        '1234567890'
        >>> st.extract_chars(['alphabet'])
        'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
        >>> st.extract_chars(['symbol', 'number'])
        '-=\\\\`[];\\',./!@#$%^&*()_+|~{}:"<>?1234567890'
        >>> extract_chars([])
        ''
        '''

        extracted = str()
        regexes = {
            'symbol': r'[ -\/:-@\[-`{-~]',
            'number': '[0-9]',
            'alphabet': '[a-zA-Z]'
        }

        for target in targets:
            regex = regexes[target]
            extracted += ''.join(re.findall(regex, SimpleTyping.CHARS))
        return extracted

    def get_random_indexes(self, chars):
        '''| ランダムにindexを生成する.
        | 生成する長さは引数に指定された文字列の長さと同じになる.
        | indexにはかぶりが無いように生成される.

        Args:
            :chars str: 文字列
        Returns:
            :list: indexのリスト

        >>> st = SimpleTyping()
        >>> result = st.get_random_indexes('abcdefghijklmnopqrstuvwxyz')
        >>> len(result)
        26
        >>> exclude_duplication = set(result)
        >>> len(result) == len(exclude_duplication)
        True
        '''

        indexes = list()

        while len(indexes) < len(chars):
            randindex = random.randint(0, len(chars) - 1)
            if not randindex in indexes:
                indexes.append(randindex)
        return indexes

    def sort_chars_from_indexes(self, extracted_chars, indexes):
        '''indexesに指定された並び順に文字列を並び替える.

        Args:
            :extracted_chars str: ランダマイズ対象の文字列
            :indexes list: 並び順のリスト

        Returns:
            :str: indexesの並び順となった文字列

        >>> st = SimpleTyping()
        >>> st.sort_chars_from_indexes('abcdef', [2, 1, 4, 3, 0, 5])
        'cbedaf'
        '''

        return ''.join([extracted_chars[index] for index in indexes])

    def get_key_char(self, key):
        '''| 入力されたキーに対応する文字を返す.
        | shiftキーが入力されている状態の場合は,shiftを押されたときの文字を返す.

        Args:
            :key object: pynput.keyboardのオブジェクト

        Returns:
            :str: 入力された文字列
        '''

        # shiftキーが押されていない場合そのまま返す.
        if self.current == set():
            return key.char

        index = SimpleTyping.CHARS.index(key.char)
        shift_index = index + int(len(SimpleTyping.CHARS) / 2)
        return SimpleTyping.CHARS[shift_index]

    def compare_key_input(self, chars, key_char):
        '''| 引数に指定された文字列の先頭と,入力文字列を比較する.
        | 比較した結果,一致する場合は先頭文字列を排除した文字列を返却.
        | 一致しなかった場合は文字列をそのまま返却する.

        Args:
            :chars str: 比較文字列
            :key_char str: 比較文字

        Returns:
            :str: 比較後文字列
        '''

        first_char = chars[0]
        if first_char != key_char: return chars
        return chars[1:]

    def modify_random_chars_by_compared_chars(self, compared_chars):
        '''| 比較後の文字列でランダム文字列を書き換える.
        | 正しいキーが入力された場合は比較後文字列とランダム文字列は異なるため,
        | 内容が変更される.
        | 内容に変更があればTrue, 内容に変更がなければFalseを返す.

        Args:
            :compared_chars str: 比較後文字列

        Returns:
            :bool: True -> 変更有, False -> 変更無
        '''

        if compared_chars != self.random_chars:
            self.random_chars = compared_chars
            return True
        return False

    def check_the_answer_for_key(self, is_pass):
        '''表示文字に対応したキーが押されたかを判定した文字列を返却する.

        Args:
            :is_pass bool: True -> OK, False -> NG

        Returns:
            :str: FINISH or OK or NG
        '''

        if len(self.random_chars) == 0: return 'FINISH'
        if is_pass: return 'OK'
        return 'NG'

    def append_records(self, expect_char, press_key_char, is_pass):
        '''| キータイプ時に下記の情報を記録するための関数.
        | self.recordsを書き換える.

        .. code-block:: python

            {
                'expect': '画面に表示されていた文字',
                'actual': '実際にタイプされた文字', 
                'status': 'expectとactualが一致しているか否か,OKかNGが入る',
                'time':   '画面に文字が表示されてからキー入力されるまでの秒数'
            }

        Args:
            :expect_char str: 画面に表示されていた文字
            :press_key_char str: 実際にタイプされた文字
            :is_pass bool: True -> 一致, False -> 不一致
        '''

        self.records.append({
            'expect': expect_char,
            'actual': press_key_char,
            'status': 'OK' if is_pass else 'NG',
            'time'  : (self.end_time - self.start_time).total_seconds()
        })

    def execute_typing_logic(self, key):
        '''|キーが入力された後の答え合わせ,一致時の処理,タイプ時の情報記録など,
        | タイプ実行時のメインロジックを実行する.


        Args:
            :key object: pynput.keyboardのオブジェクト

        Return:
            :str: self.check_the_answer_for_keyの実行結果
        '''

        self.end_time = datetime.datetime.now()

        expect_char = self.random_chars[0]
        press_key_char = self.get_key_char(key)
        compared_chars = self.compare_key_input(self.random_chars, press_key_char)
        is_pass = self.modify_random_chars_by_compared_chars(compared_chars)
        self.append_records(expect_char, press_key_char, is_pass)
        return self.check_the_answer_for_key(is_pass)

    def save_records(self):
        '''タイピング実行時の記録をファイルに保存する.
        '''

        suffix_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = '{}/record_{}.json'.format(SimpleTyping.DATA_DIR, suffix_datetime)

        with open(file_name, 'w') as f:
            json.dump(self.records, f, indent=4)

    def on_press(self, key):
        '''キー入力されたときのイベント.

        Args:
            :key object: pynput.keyboardのオブジェクト

        Returns:
            :bool: False -> キー入力イベントの終了
        '''

        if key in SimpleTyping.SHIFT_KEYS: self.current.add(key)
        # charが無い場合は特殊キーなので何もせず返す.
        if not hasattr(key, 'char'): return

        result = self.execute_typing_logic(key)

        if result == 'FINISH':
            print('End')
            self.save_records()
            return False

        self.display_target_key(result)

    def on_release(self, key):
        '''|キーが離されたときのイベント.
        | Escキーが押された場合はイベントを終了する.
        | また,Shiftキーが離されたかどうかはここで確認している.

        Args:
            :key object: pynput.keyboardのオブジェクト

        Returns:
            :bool: False -> キー入力イベントの終了
        '''

        if key == Key.esc:
            return False
        try:
            self.current.remove(key)
        except KeyError:
            pass

def main():
    targets = sys.argv[1] if len(sys.argv) > 1 else ['symbol']
    st = SimpleTyping(targets)
    st.display_target_key()

    with Listener(on_press = st.on_press, on_release = st.on_release) as listener:
        listener.join()

if __name__ == '__main__':
    main()

