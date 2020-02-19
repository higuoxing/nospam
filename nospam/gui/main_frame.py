import wx
import nospam.mail as mail
import nospam.engine as engine
import nospam.engine.rule as rule

DEFAULT_RAW_EMAIL = '''From lkqyvstyles@site-personals.com  Tue Aug 27 03:56:47 2002
Return-Path: <lkqyvstyles@site-personals.com>
Delivered-To: zzzz@localhost.spamassassin.taint.org
Received: from localhost (localhost [127.0.0.1])
	by phobos.labs.spamassassin.taint.org (Postfix) with ESMTP id 4451C43F99
	for <zzzz@localhost>; Mon, 26 Aug 2002 22:56:47 -0400 (EDT)
Received: from mail.webnote.net [193.120.211.219]
	by localhost with POP3 (fetchmail-5.9.0)
	for zzzz@localhost (single-drop); Tue, 27 Aug 2002 03:56:47 +0100 (IST)
Received: from smtp.easydns.com (smtp.easydns.com [205.210.42.30])
	by webnote.net (8.9.3/8.9.3) with ESMTP id DAA29086
	for <zzzz@spamassassin.taint.org>; Tue, 27 Aug 2002 03:57:36 +0100
Received: from 218.5.132.246 (unknown [211.160.14.157])
	by smtp.easydns.com (Postfix) with SMTP id 7714C2C995
	for <zzzz@spamassassin.taint.org>; Mon, 26 Aug 2002 22:57:31 -0400 (EDT)
Received: from 55.92.178.196 ([55.92.178.196]) by smtp-server1.cfl.rr.com with QMQP; Aug, 26 2002 10:41:10 PM +1100
Received: from [46.224.35.15] by rly-xl04.mx.aol.com with smtp; Aug, 26 2002 9:33:27 PM +1200
Received: from unknown (26.113.85.29) by smtp4.cyberec.com with esmtp; Aug, 26 2002 8:57:10 PM -0100
Received: from [183.62.39.149] by m10.grp.snv.yahoo.com with QMQP; Aug, 26 2002 7:52:32 PM +0600
From: Veronica Styles <lkqyvstyles@site-personals.com>
To: zzzz@spamassassin.taint.org
Cc: 
Subject: link to my webcam you wanted 
Sender: Veronica Styles <lkqyvstyles@site-personals.com>
Mime-Version: 1.0
Content-Type: text/plain; charset="iso-8859-1"
Date: Mon, 26 Aug 2002 22:57:34 -0400
X-Mailer: eGroups Message Poster
X-Priority: 1
Message-Id: <20020827025731.7714C2C995@smtp.easydns.com>

Wanna see sexually curious teens playing with each other?

http://www.site-personals.com <-- click here=)

me and my horny girlfriends are waiting for you... we are probably eating each other out on webcam in our dormitory as ur reading this! (inbetween classes of course *wink*)

see you soon baby,
-Veronica

mcmfkhcpedgetqj'''

DEFAULT_RULES = '''
if [mail.sender] equal "lkqyvstyles@site-personals.com" then
    HAM_TF  = 0.000001
    SPAM_TF = 0.000002
end

if [mail.content] contain "inbetween" then
    HAM_TF = 0.00002
    SPAM_TF = 0.0003
end

if [mail.content] match "mcmfkhcpedgetqj" then
    HAM_TF = 0.00001
    SPAM_TF = 0.000002
end
'''

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title, size):
        '''
        MainFrame
        :param parent: TODO
        :param id: TODO
        :param title: TODO
        :param size: TODO
        '''
        wx.Frame.__init__(self, parent, id, title,
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        self.SetSize(size)
        self.Center()

        self.engine = engine.Engine([], 0.5, 0.5)
        self.rule_parser = rule.RuleParser()
        # /-----------------------------------------------------------------------------------------\
        # | | Open | Edit Rules | ...                                                               |
        # |-----------------------------------------------------------------------------------------|
        # | /-----------------------------\ /-----------------------------------------------------\ |
        # | | Rules                       | | Email                                               | |
        # | \-----------------------------/ \-----------------------------------------------------/ |
        # | /-----------------------------\ /-----------------------------------------------------\ |
        # | |                             | | Subject: blah blah                                  | |
        # | |                             | | Content:                                            | |
        # | |                             | | Hello, world                                        | |
        # | |                             | |                                                     | |
        # | |                             | \-----------------------------------------------------/ |
        # | |                             | /-----------------------------------------------------\ |
        # | |                             | | Hit Rules & Result                                  | |
        # | |                             | \-----------------------------------------------------/ |
        # | |                             | /-----------------------------------------------------\ |
        # | |                             | |                                                     | |
        # | |                             | |                                                     | |
        # | \-----------------------------/ \-----------------------------------------------------/ |
        # \-----------------------------------------------------------------------------------------/

        # /-----------------------------------------------------------------------------------------\
        # | /--------------------------------------\ /--------------------------------------------\ |
        # | | (10, 10)                             | | (605, 10)                                  | |
        # | \--------------------------------------/ \--------------------------------------------/ |
        # \-----------------------------------------------------------------------------------------/
        self.rules_label = wx.StaticText(
            self, label='Rules Editor', pos=(10, 10), size=(585, 25))
        self.rules_label.SetFont(self.get_default_font(20))

        self.email_label = wx.StaticText(
            self, label='Email', pos=(605, 10), size=(585, 25))
        self.email_label.SetFont(self.get_default_font(20))

        # /-----------------------------------------------------------------------------------------\
        # |    .                                                                                    |
        # |    .                                                                                    |
        # |    .                                                                                    |
        # | /--------------------------------------\     ...                                        |
        # | | (10, 30)                             |                                                |
        # | |                                      |                                                |
        # | \--------------------------------------/                                                |
        # |                           | Load Rules |                                                |
        # \-----------------------------------------------------------------------------------------/
        self.rules_text = wx.TextCtrl(self, pos=(
            10, 30), size=(580, 720), style=wx.TE_MULTILINE)
        self.rules_text.SetFont(self.get_default_font(12))
        self.rules_text.Clear()
        self.rules_text.WriteText(self.load_default_rules())

        self.load_rule_button = wx.Button(
            self, label='Load Rules', pos=(440, 750), size=(150, 30))
        self.load_rule_button.Bind(wx.EVT_BUTTON, self.load_rules)

        self.email_text = wx.TextCtrl(self, pos=(605, 30), size=(
            580, 340), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.email_text.SetFont(self.get_default_font(11))
        self.email_text.Clear()
        self.email_text.WriteText(self.load_default_email())

        self.load_email_button = wx.Button(
            self, label='Load Email', pos=(885, 370), size=(150, 30))

        self.test_email_button = wx.Button(
            self, label='Test Email', pos=(1035, 370), size=(150, 30))
        self.test_email_button.Bind(wx.EVT_BUTTON, self.test_email)

        self.hit_rules_label = wx.StaticText(
            self, label='Hit Rules', pos=(605, 400), size=(585, 25))
        self.hit_rules_label.SetFont(self.get_default_font(20))

        self.hit_rules_text = wx.TextCtrl(self, pos=(605, 425), size=(
            580, 325), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.hit_rules_text.SetFont(self.get_default_font(12))

    def load_rules(self, event):
        rules_str = self.rules_text.GetValue()
        rules = self.rule_parser.parse(rules_str)
        self.engine.load_rules(rules)
        result_str = '============== Load Rules ===============\n\n'

        for r in rules:
            result_str += str(r)
        
        self.hit_rules_text.WriteText(result_str)

    def test_email(self, event):
        result = self.engine.test_mail(self.email)
        self.hit_rules_text.Clear()
        result_str = 'Is spam? ' + str(result[0]) + '\n' + \
            'Posibility: ' + str(result[1]) + '\n' + \
            '=============== Hit Rules ===============\n\n'
        for hit_rule in result[2]:
            result_str += str(hit_rule)

        self.hit_rules_text.WriteText(result_str)

    def load_default_email(self):
        self.email = mail.from_string(DEFAULT_RAW_EMAIL)
        return \
            'Subject: ' + self.email.subject + '\n' + \
            'From: ' + self.email.sender + '\n' + \
            'To: ' + self.email.receiver + '\n' + \
            'Content:\n' + self.email.content + '\n'

    def load_email(self, event):
        pass

    def get_default_font(self, font_size):
        return wx.Font(font_size, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

    def load_default_rules(self):
        return DEFAULT_RULES
