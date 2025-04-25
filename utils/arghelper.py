import sys
import argparse, regex, shutil
from .logging import Format


class CliArgs:
    class _CustomHelpFormatter(argparse.HelpFormatter):
        def _get_default_metavar_for_optional(self, action) -> str:
            return action.type.__name__

        def _get_default_metavar_for_positional(self, action) -> str:
            return action.type.__name__

        def _fill_text(self, text, width, indent) -> str:
            return "".join(indent + line for line in text.splitlines(keepends=True))

        def _get_help_string(self, action) -> str:
            help = action.help
            if "%(default)" not in action.help:
                if (
                    action.default != argparse.SUPPRESS
                    and type(action) is not argparse._StoreFalseAction
                    and type(action) is not argparse._StoreTrueAction
                ):
                    defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                    if action.required:
                        help = f"{Format.YELLOW}(R){Format.END} " + help
                    elif action.option_strings or action.nargs in defaulting_nargs:
                        help += f" {Format.DARK_GRAY}(default: %(default)s){Format.END}"
            return help

        def _format_usage(self, *args, **kwargs) -> str:
            text = super()._format_usage(*args, **kwargs)
            extra_args_string = '[-- <nargs: str ...> <kwargs: str=str ...>]'
            text = text.strip() + f' {extra_args_string}\n\n'
            matches = regex.finditer(r'(\]|^)(?<req>[^\[\]]+)(\[|$)', text)
            matches = [x for x in matches if x.capturesdict()['req'][0].strip() != '']
            for match in matches[::-1]:
                caps = list(zip([x[0] for x in match.allspans()], [x[0] for x in match.allcaptures()]))
                span, cap_text = caps[2]
                text = text.replace(text[span[0]:span[1]], f"{Format.BOLD}{cap_text}{Format.END}")
            return text.replace(extra_args_string, f'{Format.PURPLE}{extra_args_string}{Format.END}')

        @classmethod
        def customWidth(cls, args_column_width: int = 50, total_width: int = 150):
            try:
                width = min(shutil.get_terminal_size().columns - 2, total_width)
                kwargs = {"width": width, "max_help_position": args_column_width}
                return lambda prog: cls(prog, **kwargs)
            except TypeError:
                return cls


    def __init__(self, description: str = "", epilog: str = "", args_width: int = 50, total_width: int = 150) -> None:
        self.description = description
        self.epilog = epilog
        self.__ap = argparse.ArgumentParser(
            description = self.description,
            epilog = self.epilog,
            formatter_class = self._CustomHelpFormatter.customWidth(
                args_column_width = args_width,
                total_width = total_width
            ),
            add_help = False,
        )
        self.__groups = {}

    def parse_args(self) -> tuple[argparse.Namespace, list, dict]:
        cli_nargs, cli_kwargs = tuple(), dict()
        try:
            sys.argv = [x.strip() for x in sys.argv]
            split_index = sys.argv.index('--')
            sys.argv, extra_args = sys.argv[:split_index], sys.argv[split_index + 1:]
            cli_nargs = [x for x in extra_args if '=' not in x]
            cli_kwargs = {x.split('=')[0]:x.split('=')[1] for x in extra_args if '=' in x}
        except ValueError: pass
        return self.__getArgparseArgs(), cli_nargs, cli_kwargs

    def __getArgparseArgs(self) -> argparse.Namespace:
        ops = self.__ap.add_argument_group(f"{Format.UNDERLINE}Ops{Format.END}")
        ops.add_argument("-Q", "--quiet", action="store_true", default=False, help=f"Quiet mode. No printouts.")
        ops.add_argument("-V", "--verbose", action="store_true", default=False, help=f"Verbose mode. Extra printouts.")
        ops.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help=f"Show this help message and exit.")
        ops.add_argument("-F", "--force", action="store_true", default=False, help=argparse.SUPPRESS)
        ops.add_argument("-E", "--exception", action="store_true", default=False, help=argparse.SUPPRESS)

        return self.__ap.parse_args()

    def add_arg_group(self, id: str) -> argparse._ArgumentGroup:
        if id not in self.__groups:
            display_name = f"{Format.UNDERLINE}{id}{Format.END}"
            self.__groups[id] = (retval := self.__ap.add_argumement_group(display_name))
            return retval
        return self.__groups[id]
