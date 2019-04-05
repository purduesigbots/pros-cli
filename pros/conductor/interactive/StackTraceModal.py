import subprocess
from pathlib import Path
from typing import *

from click import Context, get_current_context

from pros.common import ui, utils
from pros.common.ui.interactive import application, components, parameters
from pros.common.ui.interactive.components import Component
from pros.conductor import Project
from pros.conductor.interactive import ExistingProjectParameter


class _ElfReporter(object):
    def __init__(self, elfs, root=None):
        if root is None:
            root = Path('.')
        # if we don't have an address for the ELF, assume it's 0xffff_ffff for now
        self.elfs = [root.joinpath(e[1]) if isinstance(e, tuple) else root.joinpath(e) for e in elfs]
        from elftools.elf.elffile import ELFFile
        ui.echo(root)
        ui.echo(self.elfs)
        self.elf_files = [ELFFile(e.open(mode='rb')) for e in self.elfs]
        self._timestamp = None

        self._addr2line = utils.find_executable('arm-none-eabi-addr2line') or utils.find_executable('addr2line')

    @property
    def timestamp(self) -> str:
        if self._timestamp is not None:
            return self._timestamp
        from elftools.common.exceptions import ELFError
        from elftools.elf.sections import SymbolTableSection
        for elf in self.elf_files:
            try:
                for symtab in elf.iter_sections():
                    if not isinstance(symtab, SymbolTableSection):
                        continue
                    syms = symtab.get_symbol_by_name('_PROS_COMPILE_TIMESTAMP')
                    if not syms or len(syms) != 1:
                        continue
                    sym_entry = syms[0].entry
                    ptr_sec = elf.get_section(sym_entry['st_shndx'])
                    off = sym_entry['st_value'] - ptr_sec.header['sh_addr']
                    from struct import unpack
                    str_addr = unpack('<I', ptr_sec.data()[off:off + 4])[0]
                    for sec in elf.iter_sections():
                        if sec.header['sh_addr'] <= str_addr <= sec.header['sh_addr'] + sec.header['sh_size']:
                            off = str_addr - sec['sh_addr']
                            from elftools.common.utils import parse_cstring_from_stream
                            sec.stream.seek(0)
                            s = parse_cstring_from_stream(sec.stream, sec.header['sh_offset'] + off)
                            if s:
                                self._timestamp = s.decode('utf-8')
            except ELFError:
                continue
        self._timestamp = self._timestamp or 'Unknown compile timestamp!'
        return self._timestamp

    def addr2line(self, address):
        if isinstance(address, str):
            try:
                if address.startswith('0x'):
                    address = int(address[2:], 16)
                else:
                    address = int(address)
            except ValueError:
                return None
        for elf in self.elfs:
            print([self._addr2line, '-e', str(elf), '-fapsC', f'0x{address:x}'])
            p = subprocess.run([self._addr2line, '-e', str(elf), '-fapsC', f'0x{address:x}'],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               encoding='utf-8')
            if p.returncode == 0:
                return p.stdout.strip()
        return f'Unknown address: {address:x}'

    def parse_dump(self, dump: str) -> List[str]:
        start = dump.find('BEGIN STACK TRACE')
        if start == -1:
            start = 0
        else:
            start += len('BEGIN STACK TRACE')

        end = dump.find('END OF TRACE')
        if end == -1:
            end = len(dump)
        dump = dump[start:end]
        ui.echo(dump)
        return list(filter(bool, [self.addr2line(line.strip()) for line in dump.splitlines()]))



class StackTraceModal(application.Modal[None]):
    @property
    def processing_project(self):
        return self._processing_project

    @processing_project.setter
    def processing_project(self, value: bool):
        self._processing_project = bool(value)
        self.redraw()

    @property
    def processing_dump(self):
        return self._processing_dump

    @processing_dump.setter
    def processing_dump(self, value: bool):
        self._processing_dump = bool(value)
        self.redraw()

    def __init__(self, ctx: Optional[Context] = None, project: Optional[Project] = None):
        super().__init__('Stack Trace')
        self.click_ctx: Context = ctx or get_current_context()
        self.project: Optional[Project] = project

        self.project_path = ExistingProjectParameter(
            str(project.location) if project else str(Path('~', 'My PROS Project').expanduser())
        )

        self.input: parameters.Parameter[str] = parameters.Parameter('')
        self.report: Optional[_ElfReporter] = None
        self.sources: str = ""
        self.timestamp: str = ""

        self.detail_collapsed = parameters.BooleanParameter(False)
        self._processing_project: bool = False

        self._processing_dump: bool = False
        self.dump = ''

        cb = self.project_path.on_changed(self.project_changed, asynchronous=True)
        if self.project_path.is_valid():
            cb(self.project_path)

        self.input.on_changed(self.input_changed, asynchronous=True)

    def project_changed(self, new_project: ExistingProjectParameter):
        self.processing_project = True
        self.project = Project(new_project.value)
        elfs = self.project.elfs
        self.report = _ElfReporter(elfs, root=self.project.path)
        if len(elfs) == 0:
            self.sources = ''
        elif isinstance(elfs[0], tuple):
            self.sources = '\n'.join([str(self.project.location.joinpath(e[1])) for e in elfs])
        else:
            self.sources = '\n'.join([str(self.project.location.joinpath(e)) for e in elfs])
        self.processing_project = False
        self.input_changed(self.input)

    def confirm(self, *args, **kwargs):
        pass

    def input_changed(self, new_input: parameters.Parameter[str]):
        if self.report is None or not new_input.value:
            return
        self.processing_dump = True
        self.dump = '\n'.join(self.report.parse_dump(new_input.value.strip()))
        self.processing_dump = False

    def build_detail_container(self) -> Generator[Component, None, None]:
        if self.sources:
            yield components.Label('Sources:')
            yield components.VerbatimLabel(self.sources)
        if self.report and self.report.timestamp:
            yield components.Label(f'Compiled: {self.report.timestamp}')

    def build(self) -> Generator[Component, None, None]:
        yield components.DirectorySelector('Project Directory', self.project_path)
        if self.processing_project:
            yield components.Spinner()
        else:
            yield components.Container(*self.build_detail_container(), title='Details', collapsed=self.detail_collapsed)
        yield components.Label('Paste data abort dump below')
        yield components.TextEditor('', self.input)
        if self.processing_dump or self.processing_project:
            yield components.Spinner()
        elif self.dump:
            yield components.Label('Stack trace')
            yield components.VerbatimLabel(self.dump)
