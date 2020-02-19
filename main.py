import nospam.engine as engine
import nospam.engine.rule as rule
import nospam.mail as mail
import nospam.gui.main_frame as main_frame
import wx

if __name__ == '__main__':
    app = wx.App()
    frm = main_frame.MainFrame(None, 1, "Spam Expert", size=(1200, 800))
    frm.Show()
    app.MainLoop()
