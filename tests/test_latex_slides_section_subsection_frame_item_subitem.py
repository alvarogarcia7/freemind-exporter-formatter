import unittest

from approvaltests import verify

from tests.approval_tests.command_helper import CommandHelper


class TestLatexSlidesSectionSubsectionFrameItemSubitem(unittest.TestCase):
    command_helper = CommandHelper()

    def test_(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/mm4.mm --formatter latex_slides_section_subsection_frame_item_subitem.py""")
            )
        )


if __name__ == "__main__":
    unittest.main()
