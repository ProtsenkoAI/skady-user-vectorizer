from typing import List

from .parsed_processor_impl import ParsedProcessorImpl
from .processor_hooks import ProcessorSuccessHook
from ..executing import ParseRes


class ParsedProcessorWithHooks(ParsedProcessorImpl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._process_success_hooks: List[ProcessorSuccessHook] = []

    def add_process_success_hook(self, hook: ProcessorSuccessHook):
        self._process_success_hooks.append(hook)

    def process_success(self, res: ParseRes):
        for hook in self._process_success_hooks:
            hook.process_success(res)
        return super().process_success(res)
