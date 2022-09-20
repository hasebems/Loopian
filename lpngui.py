# -*- coding: utf-8 -*-
#
#   lpngui.py   Alpha Version
#
#   from September 10 2022 by M.Hasebe
#
import pygame as pg
from pygame.locals import *     # 定数を読み込む
import datetime

###  print(pg.font.get_fonts()) 
FONTS = ['didot', 'notosansbuhid', 'hiraginosans', 'hiraginosansgb', # 0-
    'skia', 'ptsansnarrow', 'ptserif', 'jetbrainsmono', 'notosansarmenian', # 4
    'bitstreamverasansmono', 'arialroundedmtbold', 'sfcompact', 'notosanswarangciti', # 9
    'pro', 'marion', 'estrangelomidyat', 'newyork', 'sukhumvitset', 'notosansosmanya', # 13
    'notosansmyanmar', 'jetbrainsmononl', 'charter', 'systemskrift', 'stixnonunicode', # 19
    'khmersangammn', 'chalkboardse', 'kohinoortelugu', 'sfnsmono', 'notoserifmyanmar', # 24
    'alnile', 'songtitc', 'americantypewriter', 'avenirnextcondensed', 'estrangeloantioch', # 29
    'ptserifcaption', 'notosanstaile', 'optima', 'menlo', 'songtisc', 'gohatibebzemen', # 34
    'applesdgothicneo', 'shreedevanagari714', 'avenir', 'athelas', 'geneva', 'kannadasangammn', # 40
    'systemfont', 'timesnewroman', 'kohinoordevanagari', 'verdana', 'applesdgothicneoi', # 46
    'luminari', 'helveticaneue', 'notosansglagolitic', 'avenirnext', 'notosanskannada', # 51
    'palatino', 'notosansmiao', 'applebraille', 'kohinoorgujarati', 'seravek', 'sfarabic', # 56
    'tamilmn', 'munapua', 'myanmarsangammn', 'galvji', 'couriernew', 'decotypenaskh', # 62
    'notosansavestan', 'pingfanghk', 'pingfangsc', 'mishafi', 'malayalammn', 'damascus', # 68
    'itfdevanagari', 'times', 'arialhebrewdeskinterface', 'sertomalankara', 'pingfangtc', #74
    'notosansbamum', 'trattatello', 'sfnsrounded', 'arialnarrow', 'stixintegralsupd', # 79
    'notosanssyriac', 'wingdings', 'notosanssundanese', 'waseem', 'muktamahee', 'helvetica', # 84
    'hoeflertext', 'oriyasangammn', 'damascuspua', 'georgia', 'sertomardin', 'notosanssharada',# 90
    'notosansmultani', 'gillsans', 'arial', 'telugumn', 'savoyeletcc', 'telugusangammn', # 96
    'trebuchetms', 'estrangelotalada', 'iowanoldstyle', 'notosanszawgyi', 'stixsizeonesym', # 102
    'andalemono', 'notosansegyptianhieroglyphs', 'notosanslydian', 'notosanspaucinhau', 'sinhalamn', # 107
    'estrangeloquenneshrin', 'stixintegralssm', 'futura', 'luxisans', 'courier', 'notosanslycian', # 112
    'itfdevanagarimarathi', 'sfcompactrounded', 'phosphate', 'stixsizefoursym', 'bitstreamverasans', # 118
    'notosanspalmyrene', 'stixintegralsup', 'notosanspsalterpahlavi', 'cochin', # 123
    'notosansoldnortharabian', 'ptsans', 'notosanscaucasianalbanian', 'raanana', 'rockwell', # 127
    'notosanswancho', 'euphemiaucas', 'notosansmeroitic', 'farahpua', 'baskerville', # 132
    'devanagarisangammn', 'notosansadlam', 'luxiserif', 'sertojerusalemoutline', 'stixsizetwosym',
    'notosansoldhungarian', 'laomn', 'newpeninimmt', 'notosanselbasan', 'banglamn', 'applegothic',
    'copperplate', 'notosanskayahli', 'systmovpsmo', 'notosanskhudawadi', 'estrangeloedessa',
    'bodoni72oldstyle', 'tipusdelletradelsistema', 'gurmukhimn', 'notosanscuneiform', 'notosansbatak',
    'notosanssaurashtra', 'stixgeneral', 'notosanstakri', 'thonburi', 'dincondensed', 'notosansrejang',
    'sinhalasangammn', 'snellroundhand', 'myanmarmn', 'chalkboard', 'applesymbols', 'stixsizethreesym',
    'notosansolditalic', 'nadeem', 'notosanslepcha', 'superclarendon', 'notonastaliqurduui', 'muna',
    'kefa', 'baghdad', 'ptsanscaption', 'tamilsangammn', 'notosanstagbanwa', 'khmermn', 'luximono',
    'gujaratimt', 'geezaprointerface', 'bigcaslon', 'notosanstifinagh', 'arialunicodems', 'geezapropua',
    'gujaratisangammn', 'notosanslineara', 'ptmono', 'notosansoldpermic', 'bitstreamveraserif',
    'eastsyriacadiabene', 'std', 'notosansmandaic', 'ayuthaya', 'arialblack', 'diwankufipua', 'sana',
    'notosanslinearb', 'notosansmongolian', 'oriyamn', 'applemyungjo', 'notosansbhaiksuki',
    'granthasangammn', 'notosanssylotinagri', 'hiraginosansgbinterface', 'notosanssorasompeng',
    'gb18030bitmap', 'sertobatnan', 'inaimathi', 'notosanslimbu', 'notosanscoptic', 'kufistandardgk',
    'markerfelt', 'notosansinscriptionalparthian', 'lucidagrande', 'notosansgothic', 'baghdadpua',
    'dinalternate', '', 'arialhebrewscholar', 'estrangelonisibin', 'notosanstaitham', 'savoyelet',
    'albayanpua', 'notosansoldturkic', 'lastresort', 'aqua', 'brushscriptmt', 'pron', 'kohinoorbangla',
    'geezapro', 'sertokharput', 'albayan', 'gurmukhisangammn', 'monaco', 'banglasangammn',
    'notonastaliqurdu', 'notosansmarchen', 'wingdings2', 'arialhebrew', 'notosansugaritic',
    'altarikhpua', 'wingdings3', 'tahoma', 'papyrus', 'lucidagrandeui', 'nadeempua', 'alnilepua',
    'farah', 'chalkduster', 'notosansmendekikakui', 'notosanskaithi', 'diwankufi', 'comicsansms',
    'kannadamn', 'applecoloremoji', 'microsoftsansserif', 'notosansnabataean', 'krungthep', 'farisi',
    'signpainter', 'notosansphagspa', 'kufistandardgkpua', 'sertourhoy', 'stixsizefivesym', 'impact',
    'notosansthaana', 'malayalamsangammn', 'notosansyi', 'noteworthy', 'notosanscham', 'notosanskharoshthi',
    'zapfino', 'notosanstagalog', 'notosanshanifirohingya', 'notosanscypriot', 'stixintegralsd',
    'notosansmeeteimayek', 'silom', 'keyboard', 'notoserifahom', 'notosanshatran', 'notosanslisu',
    'academyengravedlet', 'kokonor', 'kailasa', 'sertojerusalem', 'notosansnko', 'notosansnewa',
    'estrangeloturabdin', 'notosanskhojki', 'notosansmro', 'notosansmodi', 'mshtakan', 'corsivahebrew',
    'notosansmanichaean', 'notosansolchiki', 'notosansosage', 'notosansbuginese', 'stixvariants',
    'notosansbassavah', 'gurmukhimt', 'bradleyhand', 'hiraginokakugothicinterface', 'notosansjavanese',
    'notosanssamaritan', 'bodoni72', 'beirut', 'notosanstirhuta', 'stdn', 'notosansoriya', 'notosanssiddham',
    'estrangelonisibinoutline', 'notosansoldpersian', 'notosansmahajani', 'notosanshanunoo', 'sanapua',
    'eastsyriacctesiphon', 'notoserifyezidi', 'laosangammn', 'notosansmasaramgondi', 'altarikh',
    'notosansnewtailue', 'notosansgunjalagondi', 'symbol', 'bodoniornaments', 'applechancery',
    'decotypenaskhpua', 'notosanspahawhhmong', 'devanagarimt', 'notosansoldsoutharabian',
    'notosansimperialaramaic', 'beirutpua', 'notosansinscriptionalpahlavi', 'applecoloremojiui', 'sathu',
    'herculanum', 'notosansvai', 'stixintegralsupsm', 'notosansbrahmi', 'notosansduployan', 'stsong',
    'plantagenetcherokee', 'notosansphoenician', 'diwanthuluth', 'notosanstaiviet', 'notosanschakma',
    'notoserifbalinese', 'notosanscarian', 'zapfdingbats', 'webdings', 'mishafigold', 'partylet', 'bodoni72smallcaps']

# Text scroll area center of the window
class LpnScroll:
    COLOR_BOX = (50,50,50)
    COLOR_INPUTS = (255,255,255)
    FONT_SIZE = 16
    LETTER_WIDTH = 10
    TEXT_OFS_X = 5
    TEXT_OFS_Y = 5

    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)
        self.text_set = []
        self.txt_surface = []
        self.font = pg.font.SysFont(FONTS[116], self.FONT_SIZE) # Courier

    def show_text(self, text, cmd):
        self.text_set.append([text,cmd])
        self.txt_surface = []

    def update(self):
        if len(self.txt_surface) == 0:
            for set in self.text_set[-10:]:
                color = (255,0,255)
                if set[1]: color = (255,255,255)
                self.txt_surface.append(self.font.render(set[0], True, color))

    def draw(self, screen):
        # Blit the rect.
        #pg.draw.rect(screen, self.color, self.rect, 2)
        pg.draw.rect(screen, self.COLOR_BOX, self.rect)
        # Blit User text.
        for num, surface in enumerate(self.txt_surface):
            screen.blit(surface,
                (self.rect.x + self.TEXT_OFS_X,
                 self.rect.y + self.TEXT_OFS_Y + 24*num)
            )

# Text input space below the window
class LpnInputBox:

    COLOR_BOX = (50,50,50)
    COLOR_INPUTS = (255,255,255)
    COLOR_PROMPT = (0,200,200)
    FONT_SIZE = 16
    LETTER_WIDTH = 10
    CURSOR_THICKNESS = 4
    CURSOR_COLOR = (160,160,160)
    TEXT_OFS_X = 5
    TEXT_OFS_Y = 5

    def __init__(self, parent, x, y, w, h=28, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = self.COLOR_INPUTS
        self.text = text
        self.font = pg.font.SysFont(FONTS[116], self.FONT_SIZE) # Courier
        self.txt_surface = self.font.render(text, True, self.color) # True/False:境界がなめらか
        self.prompt_font = pg.font.SysFont(FONTS[116], self.FONT_SIZE)
        self.active = False
        self.cursor_blink = False
        self.cursor_left = False
        self.cursor_right = False
        self.cursor_location = 0
        self.shift_key = False
        self.old_time = 0
        self.parent = parent
        self.history_position = 0   # history function
        self.input_history = []     # history function
        self.part_text = 'L1>'

    def _detect_cursor_location(self, right=False):
        txt_len = len(self.text)
        if right and self.cursor_location < txt_len:
            self.cursor_location += 1
        elif self.cursor_right and self.shift_key:
            self.cursor_location = txt_len
        elif self.cursor_left and self.shift_key:
            self.cursor_location = 0
        elif self.cursor_right and self.cursor_location < txt_len:
            self.cursor_location += 1
        elif self.cursor_left and self.cursor_location > 0:
            self.cursor_location -= 1

    def activate(self):
        self.active = True

    def set_part_text(self, num):
        if   num == 0: self.part_text = 'L1>'
        elif num == 1: self.part_text = 'L2>'
        elif num == 2: self.part_text = 'R1>'
        elif num == 3: self.part_text = 'R2>'

    def _key_ev_backspace(self):
        txt_len = len(self.text)
        if self.cursor_location == 0:
            pass
        elif txt_len < self.cursor_location:
            self.text = self.text[:-1]
            self.cursor_location -= 1
        else:
            self.text = self.text[:self.cursor_location-1] + self.text[self.cursor_location:]
            self.cursor_location -= 1
        self.txt_surface = self.font.render(self.text, True, self.color)

    def _key_ev_return(self):
        print(self.text)    # debug
        if self.text == 'quit' or self.text == 'exit':
            return True

        self.parent.input_text(self.text, True)
        self.input_history.append(self.text)
        self.text = ''
        self.cursor_location = 0
        self.history_position = 0
        self.txt_surface = self.font.render(self.text, True, self.color)
        return False

    def _select_from_history(self, step):
        max_history = len(self.input_history)
        self.history_position += step
        if self.history_position < 0:
            self.history_position = 0
        elif self.history_position > max_history:
            self.history_position = max_history
        if self.history_position == 0:
            self.text = ''
        else:
            self.text = self.input_history[max_history-self.history_position]
        self.txt_surface = self.font.render(self.text, True, self.color)
        if len(self.text) < self.cursor_location:
            self.cursor_location = len(self.text)

    def _key_ev_normal(self, event):
        # insert one letter to text
        txt_list = list(self.text)
        txt_list.insert(self.cursor_location, event.unicode)
        self.text = ''.join(txt_list)
        self._detect_cursor_location(True)
        # Re-render the text.
        self.txt_surface = self.font.render(self.text, True, self.color)

    def handle_event(self, event):
        if not self.active: return False

        if event.type == pg.KEYDOWN:
            #print(event.key)
            if event.key == pg.K_RETURN:
                return self._key_ev_return()
            elif event.key == pg.K_BACKSPACE:
                self._key_ev_backspace()
            elif event.key == pg.K_LEFT:
                self.cursor_left = True
                self._detect_cursor_location()
            elif event.key == pg.K_RIGHT:
                self.cursor_right = True
                self._detect_cursor_location()
            elif event.key == pg.K_UP:
                self._select_from_history(1)
            elif event.key == pg.K_DOWN:
                self._select_from_history(-1)
            elif event.key == pg.K_RSHIFT:
                self.shift_key = True
            elif event.key == pg.K_LSHIFT:
                self.shift_key = True
            elif event.key == pg.K_RCTRL: pass
            elif event.key == pg.K_LCTRL: pass
            elif event.key == pg.K_RALT: pass
            elif event.key == pg.K_LALT: pass
            elif event.key == pg.K_TAB: pass
            elif event.key == pg.K_ESCAPE: pass  
            else:
                self._key_ev_normal(event)

        elif event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                self.cursor_left = False
                self._detect_cursor_location()
            elif event.key == pg.K_RIGHT:
                self.cursor_right = False
                self._detect_cursor_location()
            elif event.key == pg.K_RSHIFT:
                self.shift_key = False
            elif event.key == pg.K_LSHIFT:
                self.shift_key = False
        return False

    def update(self, time):
        self.cursor_blink = True if time%10 > 2 else False
        if self.cursor_left or self.cursor_right:
            # cursor auto inc/dec
            while time > self.old_time + 2:
                self._detect_cursor_location()
                self.old_time += 2
        else:
            self.old_time = time
        
    def draw(self, screen):
        # Blit the rect.
        #pg.draw.rect(screen, self.color, self.rect, 2)
        pg.draw.rect(screen, self.COLOR_BOX, self.rect)
        # Blit User text.
        screen.blit(self.txt_surface, 
            (self.rect.x + self.TEXT_OFS_X + self.LETTER_WIDTH*3,
             self.rect.y + self.TEXT_OFS_Y)
        )
        # Blit Prompt text.
        screen.blit(self.prompt_font.render(self.part_text, True, self.COLOR_PROMPT),
            (self.rect.x + self.TEXT_OFS_X,
             self.rect.y + self.TEXT_OFS_Y)
        )
        # Blit cursor.
        if self.cursor_blink:   # display cursor
            cursor = pg.Rect(
                self.rect.left + self.TEXT_OFS_X + self.LETTER_WIDTH*3 + 1
                + self.cursor_location*self.LETTER_WIDTH,
                self.rect.top + self.rect.height - self.CURSOR_THICKNESS - 2,
                self.LETTER_WIDTH - 2, # 1 shorter than letter both sides
                self.CURSOR_THICKNESS)
            pg.draw.rect(screen, self.CURSOR_COLOR, cursor)


# White(gray) text space above the window
class LpnGuiText:

    def __init__(self, x, y, w=180, h=30, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.font = pg.font.SysFont(FONTS[116], 16)
        self.txt_surface = self.font.render(text, True, (0,0,0))

    def set_text(self, text):
        self.text = text
        self.txt_surface = self.font.render(text, True, (0,0,0))

    def update(self):
        # self.set_text(datetime.datetime.now().strftime("%H:%M:%S"))
#        self.txt_surface = self.font.render(self.text, True, (0,0,0))
        pass

    def draw(self, screen):
        # Blit the rect.
        pg.draw.rect(screen, (180,180,180), self.rect, border_radius = 7)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+10, self.rect.y+7))


# Assembly All GUI parts
class LpnGui:

    SURFACE_X_SZ = 900  #   Window Size
    SURFACE_Y_SZ = 480  #   Window Size

    # 縦の位置
    LINE1_Y = 10
    LINE2_Y = 50
    LINE3_Y = 100
    LINE4_Y = 150
    LAMP_OFS = 10

    COLUMN1_X = 30
    COLUMN2_X = 250
    COLUMN3_X = 470
    COLUMN4_X = 690
    COLUMN29_X = 460
    COLUMN39_X = 680
    COLUMN35_X = 570
    COLUMN45_X = 790
    LAMP_INTERVAL = 40
    PART_INTERVAL = 40

    def __init__(self, loop_enable, cmd):
        pg.init()
        self.screen = pg.display.set_mode((self.SURFACE_X_SZ, self.SURFACE_Y_SZ))
        pg.display.set_caption("Loopian")    # タイトル文字を指定
        self.raw_time = 0
        self._100ms_time = 0
        self.loop_enable = loop_enable
        self.cmd = cmd
        self.cmd.set_gui(self)

        self.font = pg.font.Font(None, 28)   # フォントの設定
        self.scroll_box = LpnScroll(self.COLUMN1_X, self.SURFACE_Y_SZ-330, self.SURFACE_X_SZ-60, 250)
        self.inputBox = LpnInputBox(self, self.COLUMN1_X, self.SURFACE_Y_SZ-60, self.SURFACE_X_SZ-60)
        self.inputBox.activate()

        self.dateBox = LpnGuiText(self.COLUMN1_X, self.LINE2_Y)
        self.timeBox = LpnGuiText(self.COLUMN2_X, self.LINE2_Y)
        self.bpmBox =  LpnGuiText(self.COLUMN3_X, self.LINE2_Y)
        self.beatBox = LpnGuiText(self.COLUMN4_X, self.LINE2_Y)
        self.keyBox =  LpnGuiText(self.COLUMN1_X, self.LINE3_Y)
        self.xxxBox =  LpnGuiText(self.COLUMN2_X, self.LINE3_Y)
        self.lptBox =  LpnGuiText(self.COLUMN29_X, self.LINE3_Y, 90)
        self.l2ptBox =  LpnGuiText(self.COLUMN35_X, self.LINE3_Y, 90)
        self.rptBox =  LpnGuiText(self.COLUMN39_X, self.LINE3_Y, 90)
        self.r2ptBox =  LpnGuiText(self.COLUMN45_X, self.LINE3_Y, 90)

        # Title
        font = pg.font.SysFont(FONTS[136], 32)
        self.title_text = font.render('Loopian', True, (255,255,255))


    def change_part(self, part):
        self.inputBox.set_part_text(part)

    def input_text(self, text, cmd=False):
        self.scroll_box.show_text(text, cmd)
        if cmd:
            self.cmd.start_parsing(text) # input command

    def _make_time(self):
        tm = pg.time.get_ticks()
        while tm - self.raw_time > 100:
            self._100ms_time += 1
            self.raw_time += 100
        return self._100ms_time

    def _update_display(self, current_time, seq):
        self.inputBox.update(current_time)
        self.scroll_box.update()
        self.timeBox.set_text(datetime.datetime.now().strftime("%H:%M:%S"))
        self.dateBox.set_text(str(datetime.date.today()))
        self.bpmBox.set_text('bpm: ' + str(seq.bpm))
        msr, beat, tick, count = seq.get_tick()
        self.beatBox.set_text(str(msr+1) + ' : ' + str(beat+1) + ' : ' + str(tick))
        self.keyBox.set_text('key: ' + seq.key_text)
        a,b = seq.sqobjs[0].get_loop_info()
        self.lptBox.set_text( 'L1: ' + str(a) + '/' + str(b))
        a,b = seq.sqobjs[1].get_loop_info()
        self.l2ptBox.set_text('L2: ' + str(a) + '/' + str(b))
        a,b = seq.sqobjs[2].get_loop_info()
        self.rptBox.set_text( 'R1: ' + str(a) + '/' + str(b))
        a,b = seq.sqobjs[3].get_loop_info()
        self.r2ptBox.set_text('R2: ' + str(a) + '/' + str(b))

    def _draw(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.title_text, (400, 5))
        self.inputBox.draw(self.screen)
        self.scroll_box.draw(self.screen)
        self.timeBox.draw(self.screen)
        self.dateBox.draw(self.screen)
        self.bpmBox.draw(self.screen)
        self.beatBox.draw(self.screen)
        self.keyBox.draw(self.screen)
        self.xxxBox.draw(self.screen)
        self.rptBox.draw(self.screen)
        self.r2ptBox.draw(self.screen)
        self.lptBox.draw(self.screen)
        self.l2ptBox.draw(self.screen)


    def loop(self, seq):
        clock = pg.time.Clock()
        while self.loop_enable.running:
            clock.tick(30)     # 30FPS
            current_time = self._make_time()

            # イベントを処理
            for event in pg.event.get():
                quit = self.inputBox.handle_event(event)
                if event.type == QUIT or quit:
                    pg.quit()   # Pygameの終了（画面を閉じる）
                    self.loop_enable.running = False
                    return

            self._update_display(current_time, seq)
            self._draw()
            pg.display.update()