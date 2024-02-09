import unittest

from ocdb import material, processing


class TestProcessingStepFactory(unittest.TestCase):
    def setUp(self):
        self.factory = processing.ProcessingStepFactory()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_processing_step_factory(self):
        self.assertIsInstance(
            self.factory, material.AbstractProcessingStepFactory
        )

    def test_get_processing_step_returns_processing_step(self):
        self.assertIsInstance(
            self.factory.get_processing_step(), processing.ProcessingStep
        )


class TestProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing_step = processing.ProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_processing_step(self):
        self.assertIsInstance(
            self.processing_step, material.AbstractProcessingStep
        )

    def test_has_attributes(self):
        attributes = [
            "data",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.processing_step, attribute))

    def test_process_returns_data(self):
        self.assertIsInstance(self.processing_step.process(), material.Data)
