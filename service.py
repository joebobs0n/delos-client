#!/usr/bin/python

import sys
sys.dont_write_bytecode = True

from pathlib import Path
import datetime, _io, argparse

from utils import (
    Format, LogParent, Timer,
    SuppressPrintouts,
    CliArgs,
    # RedirectPrintouts,
)

from api import app
import uvicorn

class log(LogParent):
    @classmethod
    def _call(cls, *nargs, **kwargs) -> None:
        local_nargs = kwargs['all_args'].pop('nargs')
        local_kwargs = {
            **{'calledname': calledname, 'scriptname': scriptname, 'verbose': args.verbose, 'force': args.force},
            **{x : y for x, y in kwargs['all_args'].items() if x not in ['__class__', 'cls']},
        }
        kwargs['method'](*local_nargs, **local_kwargs)

    @classmethod
    def info(cls, *nargs, sep: str = " ", end: str = "\n", flush: bool = False, stream: _io._TextIOBase = None) -> None:
        cls._call(method=super().info, all_args=locals())

    @classmethod
    def verbose(cls, *nargs, sep: str = " ", end: str = "\n", flush: bool = False, stream: _io._TextIOBase = None) -> None:
        cls._call(method=super().verbose, all_args=locals())

    @classmethod
    def warning(cls, *nargs, sep: str = " ", end: str = "\n", flush: bool = False, stream: _io._TextIOBase = None) -> None:
        cls._call(method=super().warning, all_args=locals())

    @classmethod
    def fatal(cls, *nargs, sep: str = " ", end: str = "\n", flush: bool = False, stream: _io._TextIOBase = None, err_code: int = 1) -> None:
        cls._call(method=super().fatal, all_args=locals())


def arg_defs() -> CliArgs:
    cliargs = CliArgs(args_width = 50, total_width = 150)
    cliargs.description = f"{Format.BOLD}{Format.DARK_GREEN}Delos Client Entrypoint{Format.END}"
    cliargs.epilog = f""

    xor = cliargs.add_arg_group("XOR Arguments")
    opt = xor.add_mutually_exclusive_group()
    opt.add_argument("--foo", action="store_true", help="Foo option")
    opt.add_argument("--bar", action="store_true", help="Bar option")

    # args = cliargs.add_arg_group("Arguments")

    flgs = cliargs.add_arg_group("Flags")
    flgs.add_argument("-D", "--dev", action="store_true", help="Enable development mode")

    return cliargs

def main(*nargs, **kwargs) -> None:
    uvicorn.run(
        "api:app" if args.dev else app,
        reload=True if args.dev else False,
        host="127.0.0.1",
        port=8001,
    )

if __name__ == "__main__":
    uniq = datetime.datetime.now().strftime("%m%d%y-%H%M%S")

    calledpath = Path(sys.argv[0])
    calledname = calledpath.stem
    calleddir  = calledpath.parent
    localdir   = calleddir.resolve()

    scriptpath = Path(__file__).resolve()
    scriptname = scriptpath.stem
    scriptdir  = scriptpath.parent

    args, nargs, kwargs = arg_defs().parse_args()

    with SuppressPrintouts(args.quiet, args.quiet), Timer(f"{Format.BLUE}Runtime{Format.END}"):
        try: main(*globals().pop("nargs"), **globals().pop("kwargs"))
        except KeyboardInterrupt as e:
            if args.exception: raise e
            log.warning(f"Cancelled by user")
