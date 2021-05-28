from __future__ import print_function
from datetime import datetime
import asyncore
from smtpd import SMTPServer

class EmlServer(SMTPServer):
    no = 0
    def process_message(self, peer, mailfrom, rcpttos, data,mail_options=None,rcpt_options=None):
        filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),
                self.no)
        f = open(filename, 'w')
        f.write(data)
        f.close
        print('%s saved.' % filename)
        self.no += 1


def run():
    # start the smtp server on localhost:1025
    foo = EmlServer(('localhost', 1025), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()

# smtp_server.py
import smtpd
import asyncore
import threading

class CustomSMTPServer(smtpd.SMTPServer):
  def process_message(self, peer, mailfrom, rcpttos, data):
    print('Receiving message from:', peer)
    print('Message addressed from:', mailfrom)
    print('Message addressed to:', rcpttos)
    print('Message length:', len(data))
    return

class SMTPServer():
  def __init__(self):
    self.port = 1025

  def start(self):
    '''Start listening on self.port'''
    # create an instance of the SMTP server, derived from  asyncore.dispatcher
    self.smtp = CustomSMTPServer(('0.0.0.0', self.port), None)
    # start the asyncore loop, listening for SMTP connection, within a thread
    # timeout parameter is important, otherwise code will block 30 seconds
    # after the smtp channel has been closed
    kwargs = {'timeout':1, 'use_poll': True}
    self.thread = threading.Thread(target=asyncore.loop, kwargs=kwargs)
    self.thread.start()

  def stop(self):
    '''Stop listening to self.port'''
    # close the SMTPserver to ensure no channels connect to asyncore
    self.smtp.close()
    # now it is safe to wait for asyncore.loop() to exit
    self.thread.join()

  # check for emails in a non-blocking way
  def get(self):
    '''Return all emails received so far'''
    return self.smtp.emails

if __name__ == '__main__':
  server = CustomSMTPServer(('0.0.0.0', 1025), None)
  asyncore.loop()