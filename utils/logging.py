import sys, _io
import regex, shutil


class Format:
    BULLET =  "•"        ; CLEAR =      "\033c"    ; WHITE =       "\033[097m"; WHITE_BKG =       "\033[107m";
    END =     "\033[000m"; UNDERLINE =  "\033[004m"; GRAY =        "\033[037m"; GRAY_BKG =        "\033[047m";
    BOLD =    "\033[001m"; BLINK =      "\033[005m"; DARK_GRAY =   "\033[090m"; DARK_GRAY_BKG =   "\033[100m";
    ITALICS = "\033[003m"; INVERT =     "\033[007m"; BLACK =       "\033[030m"; BLACK_BKG =       "\033[040m";

    RED =     "\033[091m"; RED_BKG =    "\033[101m"; DARK_RED =    "\033[031m"; DARK_RED_BKG =    "\033[041m";
    YELLOW =  "\033[093m"; YELLOW_BKG = "\033[103m"; DARK_YELLOW = "\033[033m"; DARK_YELLOW_BKG = "\033[043m";
    GREEN =   "\033[092m"; GREEN_BKG =  "\033[102m"; DARK_GREEN =  "\033[032m"; DARK_GREEN_BKG =  "\033[042m";
    CYAN =    "\033[096m"; CYAN_BKG =   "\033[106m"; DARK_CYAN =   "\033[036m"; DARK_CYAN_BKG =   "\033[046m";
    BLUE =    "\033[094m"; BLUE_BKG =   "\033[104m"; DARK_BLUE =   "\033[034m"; DARK_BLUE_BKG =   "\033[044m";
    PURPLE =  "\033[095m"; PURPLE_BKG = "\033[105m"; DARK_PURPLE = "\033[035m"; DARK_PURPLE_BKG = "\033[045m";

    ff_cyan = [ CYAN, DARK_CYAN ]; ff_green = [ GREEN, DARK_GREEN ]; ff_red =   [ RED, DARK_RED ]


class LogParent:
    @classmethod
    def __print_newlines(cls, msg: str, stream: _io._TextIOBase) -> str:
        if (n := regex.findall(r"^\n+", msg)):
            print(n[0], end="", file=stream)
        return regex.sub(r"^\n+", "", msg)

    @classmethod
    def __print_returns(cls, msg: str, stream: _io._TextIOBase) -> str:
        if (r := regex.findall(r"^\r+", msg)):
            w = shutil.get_terminal_size().columns - 2
            print(r[0].ljust(w, " "), end="\r", file=stream)
        return regex.sub(r"^\r+", "", msg)

    @classmethod
    def _base(cls, *nargs, **kwargs) -> None:
        flush = kwargs.get("flush", False)
        stream = kwargs.get("stream", sys.stdout)
        end = kwargs.get("end", "\n")
        pre = kwargs.get("pre", "")
        sname = kwargs.get("called_name", kwargs.get("scriptname", "_anon_"))

        msg = kwargs.get("sep", " ").join([str(x) for x in nargs])
        msg = cls.__print_newlines(msg, stream=stream)
        msg = cls.__print_returns(msg, stream=stream)
        msg = f"{pre} {Format.DARK_GRAY}[ {sname} ]{Format.END} {msg}"

        print("" if kwargs.get("plain", False) else msg, flush=flush, end=end, file=stream)

    @classmethod
    def info(cls, *nargs, **kwargs) -> None:
        kwargs = {
            **{"pre": f"{Format.GREEN}-I-{Format.END}", "stream": kwargs.get("stream") or sys.stdout},
            **kwargs,
        }
        cls._base(*nargs, **kwargs)

    @classmethod
    def verbose(cls, *nargs, **kwargs) -> None:
        if kwargs.pop("verbose"):
            kwargs = {
                **{"pre": f"{Format.PURPLE}-V-{Format.END}", "stream": kwargs.get("stream") or sys.stdout},
                **kwargs,
            }
            cls._base(*nargs, **kwargs)

    @classmethod
    def warning(cls, *nargs, **kwargs) -> None:
        kwargs = {
            **{"pre": f"{Format.YELLOW}-W-{Format.END}", "stream": kwargs.get("stream") or sys.stderr},
            **kwargs,
        }
        cls._base(*nargs, **kwargs)

    @classmethod
    def fatal(cls, *nargs, **kwargs) -> None:
        if kwargs.get("force"): cls.warning(*nargs, **kwargs); return
        kwargs = {
            **{"pre": f"{Format.RED}-F-{Format.END}", "stream": kwargs.get("stream") or sys.stderr},
            **kwargs,
        }
        cls._base(*nargs, **kwargs)
        exit(kwargs["err_code"])
