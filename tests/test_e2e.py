import unittest

from tests.approval_tests.command_helper import CommandHelper
from approvaltests import verify


class MyTestCase(unittest.TestCase):
    command_helper = CommandHelper()
    def test_leaf_as_text(self) -> None:
        verify(self.command_helper.invoke_command(self.command_helper.to_list("""\
python3 main.py --input ./data/test1.mm --formatter leaf_as_text.py""")))

    def test_leaf_as_latex_slides(self) -> None:
        verify(self.command_helper.invoke_command(self.command_helper.to_list("""\
python3 main.py --input ./data/test1.mm --formatter latex_slides.py""")))


if __name__ == '__main__':
    unittest.main()
