# -*- coding: utf-8 -*-
"""
Generic command class for commands change prompt
"""

__author__ = 'Marcin Usielski'
__copyright__ = 'Copyright (C) 2019, Nokia'
__email__ = 'marcin.usielski@nokia.com'

import abc
import six

from moler.cmd.commandtextualgeneric import CommandTextualGeneric
from moler.exceptions import ParsingDone


@six.add_metaclass(abc.ABCMeta)
class CommandChangingPrompt(CommandTextualGeneric):
    """Base class for textual commands."""

    def __init__(self, connection, expected_prompt, prompt=None, newline_chars=None, runner=None, target_newline="\n"):
        """
        Base class for textual commands which change prompt.

        :param connection: connection to device.
        :param expected_prompt: prompt on device changed by this command.
        :param prompt: expected prompt sending by device after command execution. Maybe String or compiled re.
        :param newline_chars:  new line chars on device (a list).
        :param runner: runner to run command.
        :param target_newline: newline on device when command is finished and prompt is changed.
        """
        super(CommandChangingPrompt, self).__init__(connection=connection, prompt=prompt, newline_chars=newline_chars,
                                                    runner=runner)
        self._re_expected_prompt = CommandTextualGeneric._calculate_prompt(expected_prompt)  # Expected prompt on device
        #                                                                                      after command execution.
        self.ret_required = False
        self.target_newline = target_newline

    def on_new_line(self, line, is_full_line):
        """
        Process output from device line by line.

        :param line: Line from device.
        :param is_full_line: True if line was eneded with newline char(s), False otherwise.
        :return: None
        """
        try:
            self._is_expected_prompt(line)
        except ParsingDone:
            pass  # line has been fully parsed by one of above parse-methods

    def _is_expected_prompt(self, line):
        """
        Checks if line contains expected prompt.

        :param line:
        :return: None
        :raise: ParsingDone if line contains expected prompt
        """
        if self._regex_helper.search_compiled(self._re_expected_prompt, line):
            if not self.done():
                self.set_result(self.current_ret)
                raise ParsingDone()

    @abc.abstractmethod
    def build_command_string(self):
        """
        Returns string with command constructed with parameters of object.

        :return:  String with command.
        """
