from typing import List

from .parsed_processor_impl import ParsedProcessorImpl
from .processor_hooks import ProcessorProcessHook, ProcessorProcessSuccessHook
from ..executing import ParseRes


class ParsedProcessorWithHooks(ParsedProcessorImpl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._process_hooks: List[ProcessorProcessHook] = []
        self._process_success_hooks: List[ProcessorProcessSuccessHook] = []

    def add_process_hook(self, hook: ProcessorProcessHook):
        self._process_hooks.append(hook)

    def add_process_success_hook(self, hook: ProcessorProcessSuccessHook):
        self._process_success_hooks.append(hook)

    def process(self, parsed_results: ParseRes, *args, **kwargs):
        for hook in self._process_hooks:
            hook.process(parsed_results)
        return super().process(parsed_results, *args, **kwargs)

    def process_success(self, res: ParseRes):
        for hook in self._process_success_hooks:
            hook.process_success(res)
        return super().process_success(res)
