import random

try:
    import znc
except ImportError:
    from dice.tests import mock_znc as znc
from dice import prettytable


def _mkhelp():
    headers = "Command Arguments Description".split()
    pt = prettytable.PrettyTable(headers)
    pt.align = 'l'
    pt.add_row(['Add', '<chan>', 'Enable dice in <chan>'])
    pt.add_row(['Del', '<chan>', 'Disable dice in <chan>'])
    pt.add_row(['List', '', ''])
    pt.add_row(['Help', '', 'Generate this output'])
    return pt.get_string(sortby='Command')


HELP_TXT = _mkhelp()


class dice(znc.Module):
    description = 'Dice for Kismet'

    def nv_add(self, channel):
        self.nv[channel] = '1'

    def nv_del(self, channel):
        if channel in self.nv:
            del self.nv[channel]

    def nv_list(self):
        return list(self.nv.keys())

    def cmd_add(self, line):
        channel = line.split(' ')[0]
        if not channel:
            self.PutModule('Missing argument')
        else:
            if channel in self.nv_list():
                self.PutModule('Channel already enabled')
            else:
                self.nv_add(channel)
                self.PutModule('Channel enabled')

    def cmd_del(self, line):
        channel = line.split(' ')[0]
        if not channel:
            self.PutModule('Missing argument')
        else:
            if channel in self.nv_list():
                self.nv_del(channel)
                self.PutModule('Channel disabled')
            else:
                self.PutModule('Channel not enabled')

    def cmd_list(self, line):
        chans = self.nv_list()
        if chans:
            pt = prettytable.PrettyTable(('Channel',))
            pt.align = 'l'
            for chan in chans:
                pt.add_row((chan,))
            for line in pt.get_string(sortby='Channel').splitlines():
                self.PutModule(line)
        else:
            self.PutModule('No channels enabled')

    def cmd_help(self, line):
        for line in HELP_TXT.splitlines():
            self.PutModule(line)

    def OnModCommand(self, line):
        command, _, args = line.partition(' ')
        dispatch = {
            'add': self.cmd_add,
            'del': self.cmd_del,
            'list': self.cmd_list,
            'help': self.cmd_help,
        }
        if command.lower() in dispatch:
            dispatch[command.lower()](args)
        else:
            self.PutModule('Unknown command.  Try Help.')

    def OnChanMsg(self, nick, chan, message):
        message = str(message).split(' ')
        if message[0] == '!roll' and chan.GetName() in self.nv_list():
            try:
                target_number = int(message[1])
            except (ValueError, IndexError):
                target_number = 20
            roll = random.randint(1, 20)
            success = roll <= target_number
            success_str = 'Success' if success else 'Failure'
            template = '{0} rolled {1} vs. {2}: {3}'
            output = template.format(
                nick.GetNick(),
                roll,
                target_number,
                success_str,
            )
            self.PutIRC('PRIVMSG {0} :{1}'.format(chan.GetName(), output))
        return znc.CONTINUE
