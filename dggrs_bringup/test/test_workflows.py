from pathlib import Path
import unittest


class WorkflowFilesTests(unittest.TestCase):
    def test_ci_workflow_exists_with_build_and_test_steps(self) -> None:
        workflow = Path(".github/workflows/ci.yml")
        self.assertTrue(workflow.exists())
        content = workflow.read_text()
        self.assertIn("ros-tooling/setup-ros", content)
        self.assertIn("colcon build", content)
        self.assertIn("python3 -m unittest", content)

    def test_actionlint_workflow_exists(self) -> None:
        workflow = Path(".github/workflows/actionlint.yml")
        self.assertTrue(workflow.exists())
        content = workflow.read_text()
        self.assertIn("rhysd/actionlint", content)


if __name__ == "__main__":
    unittest.main()
