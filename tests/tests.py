import unittest

from mock import MagicMock, patch, call

from open_urls import find_urls, find_tasks, process_file


class Tests(unittest.TestCase):
    def test_line_is_url(self):
        self.assertItemsEqual(find_urls('http://just.one.url.in.line.com'), [
            'http://just.one.url.in.line.com',
        ])

    def test_url_surrounded_by_text(self):
        self.assertItemsEqual(find_urls('before http://and.net after'), [
            'http://and.net',
        ])

    def test_two_urls_in_line(self):
        self.assertItemsEqual(find_urls('a https://two.com b http://urls.in.line c'), [
            'https://two.com', 'http://urls.in.line',
        ])

    def test_http_augmented(self):
        self.assertItemsEqual(find_urls('yes heikobehrens.net does work'), [
            'http://heikobehrens.net',
        ])

    def test_tasks(self):
        self.assertItemsEqual(find_tasks('before T1234 after'), [
            'https://tasks/1234',
        ])

    @patch('subprocess.call')
    def test_process_file(self, subp_call):
        infile = MagicMock()
        infile.readlines.return_value = ['line1', 'line2']
        f1 = MagicMock(side_effect=lambda s: {'f1:' + s})
        f2 = MagicMock(side_effect=lambda s: {'f2:' + s})
        subp_call.return_value = 0

        process_file(infile, [f1, f2], 'some command', False)

        self.assertEqual(f1.call_args_list, [call('line1'), call('line2')])
        self.assertEqual(f2.call_args_list, [call('line1'), call('line2')])
        self.assertItemsEqual(subp_call.call_args_list, [
            call('some command f1:line1', shell=True),
            call('some command f1:line2', shell=True),
            call('some command f2:line1', shell=True),
            call('some command f2:line2', shell=True),
        ])

    @patch('subprocess.call')
    def test_process_file_exits(self, subp_call):
        infile = MagicMock()
        infile.readlines.return_value = ['line1']
        f1 = MagicMock(side_effect=lambda s: {'f1:' + s})
        subp_call.return_value = 123

        with self.assertRaises(SystemExit):
            process_file(infile, [f1], 'some command', False)

        self.assertEqual(f1.call_args_list, [call('line1')])
        self.assertItemsEqual(subp_call.call_args_list, [
            call('some command f1:line1', shell=True),
        ])

    @patch('subprocess.call')
    @patch('__builtin__.print')
    def test_process_file_dry_run(self, sys_print, subp_call):
        infile = MagicMock()
        infile.readlines.return_value = ['line1']
        f1 = MagicMock(side_effect=lambda s: {'f1:' + s})
        subp_call.return_value = 123

        process_file(infile, [f1], 'some command', True)

        self.assertEqual(f1.call_args_list, [call('line1')])
        self.assertEqual(subp_call.call_count, 0)
        self.assertItemsEqual(sys_print.call_args_list, [
            call('some command f1:line1'),
        ])
