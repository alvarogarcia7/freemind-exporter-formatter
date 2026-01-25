import unittest

from approvaltests import verify

from tests.approval_tests.command_helper import CommandHelper


class MyTestCase(unittest.TestCase):
    command_helper = CommandHelper()

    def test_leaf_as_text(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/Freemind/test1.mm --formatter leaf_as_text.py""")
            )
        )

    def test_leaf_as_latex_slides(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/Freemind/test1.mm --formatter latex_slides.py""")
            )
        )

    def test_titles(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/Freemind/test1.mm --formatter titles.py""")
            )
        )

    def test_freeplane_leaf_as_text(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/mm1.mm --formatter leaf_as_text.py""")
            )
        )

    def test_freeplane_leaf_as_latex_slides(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/mm1.mm --formatter latex_slides.py""")
            )
        )

    def test_freeplane_titles(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/mm1.mm --formatter titles.py""")
            )
        )

    def test_mindmap_orgmode(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/mm3.mm --formatter orgmode.py""")
            )
        )

    def test_mindmap_orgmode_simple(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/orgmode_test1.mm --formatter orgmode.py""")
            )
        )

    def test_mindmap_orgmode_no_end_times(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/orgmode_test2.mm --formatter orgmode.py""")
            )
        )

    def test_mindmap_orgmode_multiple_projects(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/orgmode_test3.mm --formatter orgmode.py""")
            )
        )

    def test_mindmap_orgmode_empty_worklog(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/orgmode_test4.mm --formatter orgmode.py""")
            )
        )

    def test_mindmap_orgmode_multiple_dates(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/orgmode_test5.mm --formatter orgmode.py""")
            )
        )

    def test_mindmap_orgmode_lists(self) -> None:
        verify(
            self.command_helper.invoke_command(
                self.command_helper.to_list("""\
python3 main.py --input ./data/FreePlane/orgmode_lists/input.mm --formatter orgmode_lists.py""")
            )
        )


if __name__ == "__main__":
    unittest.main()
