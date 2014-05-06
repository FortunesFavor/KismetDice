import unittest
import random

from mock import call, Mock

from dice import dice
from dice import prettytable
# from dice.tests.mock_znc import Module, CONTINUE


class DiceTest(unittest.TestCase):
    def setUp(self):
        self.dice = dice()
        self.old_random = random.randint
        random.randint = Mock()
        random.randint.return_value = 15

    def tearDown(self):
        random.randint = self.old_random

    def mock_commands(self):
        self.dice.cmd_add = Mock()
        self.dice.cmd_del = Mock()
        self.dice.cmd_list = Mock()
        self.dice.cmd_help = Mock()

    def test_nv_add(self):
        self.dice.nv_add('#foo')
        self.assertEqual(self.dice.nv, {'#foo': '1'})

    def test_nv_del(self):
        self.dice.nv['#foo'] = '1'
        self.dice.nv_del('#foo')
        self.assertEqual(self.dice.nv, {})

    def test_nv_del_not_in(self):
        self.dice.nv['#bar'] = '1'
        self.dice.nv_del('#foo')
        self.assertEqual(self.dice.nv, {'#bar': '1'})

    def test_nv_list(self):
        self.dice.nv['#foo'] = '1'
        l = self.dice.nv_list()
        self.assertEqual(l, list(self.dice.nv.keys()))

    def test_cmd_add_blank_input(self):
        self.dice.cmd_add('')
        self.dice.PutModule.assert_called_once_with('Missing argument')

    def test_cmd_add_channel_exists(self):
        self.dice.nv['#foo'] = '1'
        self.dice.cmd_add('#foo')
        self.dice.PutModule.assert_called_once_with('Channel already enabled')

    def test_cmd_add(self):
        self.dice.cmd_add('#foo')
        self.dice.PutModule.assert_called_once_with('Channel enabled')
        self.assertEqual(self.dice.nv, {'#foo': '1'})

    def test_cmd_del_blank_input(self):
        self.dice.cmd_del('')
        self.dice.PutModule.assert_called_once_with('Missing argument')

    def test_cmd_del_not_existant(self):
        self.dice.cmd_del('#foo')
        self.dice.PutModule.assert_called_once_with('Channel not enabled')

    def test_cmd_del(self):
        self.dice.nv['#foo'] = '1'
        self.dice.nv['#bar'] = '1'
        self.dice.cmd_del('#foo')
        self.dice.PutModule.assert_called_once_with('Channel disabled')
        self.assertEqual(self.dice.nv, {'#bar': '1'})

    def test_cmd_list_empty(self):
        self.dice.cmd_list('')
        self.dice.PutModule.assert_called_once_with('No channels enabled')

    def test_cmf_list(self):
        pt = prettytable.PrettyTable(('Channel',))
        pt.add_row(('#foo',))
        pt.align = 'l'
        lines = pt.get_string(sortby='Channel').splitlines()
        lines = [call(x) for x in lines]
        self.dice.nv['#foo'] = '1'
        self.dice.cmd_list('')
        actual = self.dice.PutModule.call_args_list
        self.assertEqual(actual, lines)

    def test_cmd_help(self):
        # it is less dirty to copy than to nocover.
        headers = "Command Arguments Description".split()
        pt = prettytable.PrettyTable(headers)
        pt.align = 'l'
        pt.add_row(['Add', '<chan>', 'Enable dice in <chan>'])
        pt.add_row(['Del', '<chan>', 'Disable dice in <chan>'])
        pt.add_row(['List', '', ''])
        pt.add_row(['Help', '', 'Generate this output'])
        lines = pt.get_string(sortby='Command').splitlines()
        lines = [call(x) for x in lines]
        self.dice.cmd_help('')
        actual = self.dice.PutModule.call_args_list
        self.assertEqual(actual, lines)

    def test_omc_help(self):
        self.mock_commands()
        self.dice.OnModCommand('help')
        self.dice.cmd_help.assert_called_once_with('')

    def test_omc_invalid(self):
        self.mock_commands()
        self.dice.OnModCommand('foo')
        self.dice.PutModule.assert_called_once_with(
            'Unknown command.  Try Help.'
        )

    def test_omc_add(self):
        self.mock_commands()
        self.dice.OnModCommand('add #foo')
        self.dice.cmd_add.assert_called_once_with('#foo')

    def test_onchan_invalid(self):
        chan_mock = Mock()
        chan_mock.GetName.return_value = '#foo'
        nick_mock = Mock()
        nick_mock.GetNick.return_value = 'Tritium'
        message = 'something not starting with !roll'
        self.dice.OnChanMsg(nick_mock, chan_mock, message)
        assert not self.dice.PutIRC.called, "PutIRC shouldn't have been called"

    def test_onchan_noarg(self):
        chan_mock = Mock()
        chan_mock.GetName.return_value = '#foo'
        nick_mock = Mock()
        nick_mock.GetNick.return_value = 'Tritium'
        message = '!roll'
        self.dice.cmd_add('#foo')
        self.dice.OnChanMsg(nick_mock, chan_mock, message)
        expected = 'PRIVMSG #foo :Tritium rolled 15 vs. 20: Success'
        self.dice.PutIRC.assert_called_once_with(expected)

    def test_onchan_with_fourteen(self):
        chan_mock = Mock()
        chan_mock.GetName.return_value = '#foo'
        nick_mock = Mock()
        nick_mock.GetNick.return_value = 'Tritium'
        message = '!roll 14'
        self.dice.cmd_add('#foo')
        self.dice.OnChanMsg(nick_mock, chan_mock, message)
        expected = 'PRIVMSG #foo :Tritium rolled 15 vs. 14: Failure'
        self.dice.PutIRC.assert_called_once_with(expected)
