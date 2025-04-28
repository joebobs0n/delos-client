#!/usr/bin/zsh

setopt nullglob

declare -r script_path=$( [[ -L $0 ]] && readlink $0 || echo $0 )
declare -r script_name=${script_path:r:t}
declare -r script_dir=${script_path:h}
declare -r script_pname=${$( readlink ${script_dir} ):r:t}
declare -r local_dir=$( pwd )

# ? globals
function () {
    declare -rg f_bullet="•";

    declare -rg f_clear="\ec";           declare -rg f_end="\e[000m";
    declare -rg f_bold="\e[001m";        declare -rg f_underline="\e[004m";
    declare -rg f_invert="\e[003m";      declare -rg f_blink="\e[005m";

    declare -rg f_white="\e[097m";       declare -rg f_white_bkg="\e[107m";
    declare -rg f_gray="\e[037m";        declare -rg f_gray_bkg="\e[047m";
    declare -rg f_dark_gray="\e[090m";   declare -rg f_dark_gray_bkg="\e[100m";
    declare -rg f_black="\e[030m";       declare -rg f_black_bkg="\e[040m";

    declare -rg f_dark_red="\e[031m";    declare -rg f_dark_red_bkg="\e[041m";
    declare -rg f_dark_yellow="\e[033m"; declare -rg f_dark_yellow_bkg="\e[043m";
    declare -rg f_dark_green="\e[032m";  declare -rg f_dark_green_bkg="\e[042m";
    declare -rg f_dark_cyan="\e[036m";   declare -rg f_dark_cyan_bkg="\e[046m";
    declare -rg f_dark_blue="\e[034m";   declare -rg f_dark_blue_bkg="\e[044m";
    declare -rg f_dark_purple="\e[035m"; declare -rg f_dark_purple_bkg="\e[045m";

    declare -rg f_red="\e[091m";         declare -rg f_red_bkg="\e[101m";
    declare -rg f_yellow="\e[093m";      declare -rg f_yellow_bkg="\e[103m";
    declare -rg f_green="\e[092m";       declare -rg f_green_bkg="\e[102m";
    declare -rg f_cyan="\e[096m";        declare -rg f_cyan_bkg="\e[106m";
    declare -rg f_blue="\e[094m";        declare -rg f_blue_bkg="\e[104m";
    declare -rg f_purple="\e[095m";      declare -rg f_purple_bkg="\e[105m";

    declare -rg log_prefix="${f_dark_gray}[ ${script_name} ]${f_end}"
    declare -rg uniq=$( date "+%m%d%y-%H%M%S" )
    declare -rg default_err_code=1
}

function convertTime {
    local tresid thours tmins tseconds
    (( thours = ( $2 - $1 ) / 3600.0 )); tresid=$( echo "( $2 - $1 ) % 3600" | bc )
    (( tmins  = tresid / 60 ));        tseconds=$( echo "${tresid} % 60"     | bc )
    printf "%d:%02d:%09.6f\n" ${thours} ${tmins} ${tseconds}
}

function log_base {
    echo $2 | sed -r -z "s/^(\n*).*/\1/g"
    msg=$( echo -E $2 | sed -r -z 's/^(\\n)*//g' )
    echo -n "$1 ${log_prefix} "; echo $@[3,-1] ${msg}
}

function info {
    log_base "${f_green}-I-${f_end}" $@[-1] $@[1,-2]
}

function warning {
    log_base "${f_yellow}-W-${f_end}" $@[-1] $@[1,-2] >&2
}

function verbose {
    [[ ${args[verbose]} == 1 ]] && log_base "${f_purple}-V-${f_end}" $@[-1] $@[1,-2]
}

function fatal {
    [[ $@[-1] =~ ^[0-9]+$ ]] && exit_code=$@[-1] || argv+=${default_err_code}
    log_base "${f_red}-F-${f_end}" $@[-2] $@[1,-3] >&2; exit $@[-1]
}

function timeFunc {
    local tic=$( date +"%s.%N" ); $1 $@[2,-1]; local toc=$( date +"%s.%N" );
    info -n "\n${f_green}$1 ${f_default}runtime:${f_end} "; convertTime $tic $toc
}

function quietMode {
    [[ ${args[quiet]} == 1 ]] && $1 $@[2,-1] 1> /dev/null || $1 $@[2,-1]
}

function getArgAttribute {
    data=$( echo $1 | sed -z -r 's/^\s*|\s*$//g' ); attribute=$2; key=$3
    [[ $( echo ${data} | wc -l ) != 1 ]] && searchable=$( echo ${data} | grep "-${key}" ) || searchable=${data}
    [[ ${1} =~ ^%%.* || ${2} =~ ^\\s*$ ]] && return 1
    case ${attribute} in
        "key_char")                echo ${searchable}         | awk -F ";" '{print $1}'  ;;
        "key_word")                echo ${searchable}         | awk -F ";" '{print $2}'  ;;
        "dest_var")                echo ${searchable}         | awk -F ";" '{print $3}'  ;;
        "required")                echo ${searchable}         | awk -F ";" '{print $4}'  ;;
        "meta_var")                echo ${searchable}         | awk -F ";" '{print $5}'  ;;
        "nargs")                   echo ${searchable}         | awk -F ";" '{print $6}'  ;;
        "nargs_lower")  getArgAttribute ${searchable} "nargs" | awk -F "," '{print $1}'  ;;
        "nargs_upper")  getArgAttribute ${searchable} "nargs" | awk -F "," '{print $NF}' ;;
        "choices")                 echo ${searchable}         | awk -F ";" '{print $7}'  ;;
        "default")                 echo ${searchable}         | awk -F ";" '{print $8}'  ;;
        "help")                    echo ${searchable}         | awk -F ";" '{print $9}'  ;;
        "var_name")
            local tname=$( getArgAttribute $1 "dest_var" )
            [[ ${tname} =~ ^\\s*$ ]] && tname=$( getArgAttribute $1 "key_word" )
            echo ${tname}
            ;;
        "nargs_is_range")
            local nargs=$( getArgAttribute ${searchable} "nargs" )
            [[ ${nargs} =~ , ]] && echo 1 || echo 0
            ;;
        "nargs_has_top")
            local nargs=$( getArgAttribute ${searchable} "nargs" )
            local nargs_upper=$( getArgAttribute ${searchable} "nargs_upper" )
            [[ ${nargs} =~ , && ! ${nargs_upper} =~ ^\\s*$ ]] && echo 1 || echo 0
            ;;
        *) warning "undefined argument attribute request [ ${f_yellow}${attribute}${f_end} ]" ;;
    esac
    return 0
}

function printNargs {
    local lower=$( echo ${3} | awk -F "," '{print $1}' );
    local upper=$( echo ${3} | awk -F "," '{print $2}' )
    [[ ${3} =~ , ]] && local is_range=1 || local is_range=0

    if [[ ${lower} =~ \\s* ]]; then
        if [[ ${2} < ${lower} ]]; then
            echo -n " ${1} $( printNargs ${1} $(( ${2} + 1 )) ${3} )"
        else
            if [[ ${upper} =~ \\s* && ${is_range} == 1 ]]; then
                echo -n " ..."
            elif [[ ${2} < ${upper} ]]; then
                echo -n " [${1} $( printNargs ${1} $(( ${2} + 1 )) ${3} )]"
            fi
        fi
    fi
}

function genUsageStr {
    local retstr="usage: ${f_bold}${script_path:t}${f_end}"
    local required=""; local optional=""
    foreach arg_def in ${(ps:\n:)1}
        if [[ ! ${arg_def} =~ ^%% ]]; then
                key=$( getArgAttribute ${arg_def} "key_char" )
               word=$( getArgAttribute ${arg_def} "key_word" )
                req=$( getArgAttribute ${arg_def} "required" )
               type=$( getArgAttribute ${arg_def} "meta_var" )
            choices=$( getArgAttribute ${arg_def} "choices"  )
              nargs=$( getArgAttribute ${arg_def} "nargs"    )

            [[ ${choices} =~ ^\\s*$ ]] && metavar=${type} || metavar="{${choices}}"
            [[ ! ${key} =~ ^\\s*$ ]] && inner="-${key}" || inner="--${word}"

            nargsStr=$( printNargs ${metavar} 0 ${nargs} | sed -r 's/^\s*//' )
            inner=$( echo "${inner} ${nargsStr}" | sed -r 's/\s*$//g' )

            [[ ${req} != 1 ]] && optional+=" [${inner}]" || required+=" ${f_bold}${inner}${f_end}"
        fi
    end
    retstr+=" ${required} ${optional} ${f_purple}[-- <nargs: str ...> <kwargs: str=str ...>]${f_end}"
    echo "$( echo ${retstr} | sed -r 's/\s{2,}/ /g')"
}

function genHelpStr {
    local retstr=""
    echo $1 | while read -r arg_def; do
        local minfo=""
        if [[ ! ${arg_def} =~ ^%% ]]; then
            required=$( getArgAttribute ${arg_def} "required" )
               nargs=$( getArgAttribute ${arg_def} "nargs"    )
            meta_var=$( getArgAttribute ${arg_def} "meta_var" )
            key_char=$( getArgAttribute ${arg_def} "key_char" )
            key_word=$( getArgAttribute ${arg_def} "key_word" )
            help_str=$( getArgAttribute ${arg_def} "help"     )

            [[ ! ${nargs} =~ ^\\s*$ && ${required} != 1 ]] && nargs="[${nargs}]"
            if [[ ! ${meta_var} =~ ^\\s*$ ]]; then
                default=$( getArgAttribute ${arg_def} "default" )
                choices=$( getArgAttribute ${arg_def} "choices" )

                [[ ! ${default} =~ ^\\s*$ && ${required} != 1 ]] && minfo+="default: ${default} | "
                [[ ! ${choices} =~ ^\\s*$ ]] && minfo+="choices: ${choices} | "
                [[ ! ${minfo} =~ ^\\s*$ ]] && minfo="${f_dark_gray}($( echo ${minfo} | sed -r "s/^[ \|]+|[ \|]+$//g" ))${f_end}"
            fi
            [[ ! ${key_char} =~ ^\\s*$ ]] && kc_str="-${key_char} ${meta_var}" || kc_str=""
            [[ ! ${key_word} =~ ^\\s*$ ]] && kw_str="--${key_word} ${meta_var}" || kw_str=""
            retstr+="${kc_str};${kw_str};${nargs};  ${help_str} ${minfo}\n"
        else
            retstr+="%%;%%;%%;%%\n"
        fi
    done
    retstr=$( echo ${retstr} | column -ts ";" )
    retstr=$( echo ${retstr} | sed -r 's/(^\s*)-/\1  -/g' | sed -r 's/%%.*/%%/g' )
    echo ${retstr}
}

function printHelp {
     args_str=$( echo ${help_str} | sed -r -z 's/(.*)\n*%%.*/\1/g')
    flags_str=$( echo ${help_str} | sed -r -z 's/.*%%\n*(.*)/\1/g')

    echo "${usage_str}"
    [[ ! ${description} =~ ^\\s*$ ]] && echo "\n$( echo ${description} | sed -z -r 's/^\s*|\s*$//g' )"
    [[ ! ${args_str}    =~ ^\\s*$ ]] && echo "\n${f_underline}Arguments${f_end}:\n${args_str}"
    [[ ! ${flags_str}   =~ ^\\s*$ ]] && echo "\n${f_underline}Flags${f_end}:\n${flags_str}"
    [[ ! ${epilog}      =~ ^\\s*$ ]] && echo "\n$( echo ${epilog} | sed -z -r 's/^\s*|\s*$//g' )"
    exit 0
}

function dumpArgs {
    foreach k in ${(k)args}; do
        echo "  ${f_bullet} ${f_dark_cyan}${k}${f_end}%%${f_cyan}${args[${k}]}${f_end}"
    done | sort | column -ts "%%"
    exit 0
}

function validateArgs {
    foreach arg_def in ${(ps:\n:)arg_definitions}; do
        if [[ $( getArgAttribute ${arg_def} "required" ) == 1 ]]; then
            local vname=$( getArgAttribute ${arg_def} "var_name" )
            [[ ${args[${vname}]} == ${req_init} ]] && fatal "missing required argument\n${usage_str}"
        fi
    done
}

function setFlag {
    local vname=$( getArgAttribute $1 "var_name" )
    local val=$( getArgAttribute $1 "default" )
    [[ ${val} == 1 ]] && val=0 || val=1
    args[${vname}]=${val}
}

function printBadArg {
    key_char=$( getArgAttribute $1 "key_char" ); [[ ! ${key_char} =~ ^\\s*$ ]] && key_char="-${key_char}"
    key_word=$( getArgAttribute $1 "key_word" ); [[ ! ${key_word} =~ ^\\s*$ ]] && key_word="--${key_word}"
    echo "${key_char}$( [[ ! ${key_char} =~ ^\\s*$ ]] && echo "," )${key_word}"
}

function printBadNumArgs {
    bad_arg=$( printBadArg $1 ); nargs=$( getArgAttribute $1 "nargs" )
    fatal "incorrect num of args provided [ ${f_yellow}${bad_arg}${f_end} : ${f_red}${it}${f_end} : ${f_green}{${nargs}}${f_end} ]"
}

function printBadArgChoice {
    bad_arg=$( printBadArg $1 ); choices=$( getArgAttribute $1 "choices" )
    fatal "invalid choice [ ${f_yellow}${bad_arg}${f_end} : ${f_dark_green}{${choices}}${f_end} : ${f_red}${term}${f_end} ]"
}

function setVar {
    if [[ $( echo ${current_arg_def} | wc -l ) > 1 ]]; then
        local caught="${$( echo ${current_arg_def} | grep -E -o '^[^;]*;[^;]*' | tr '\n' ' ' | sed -r 's/^\s+|\s+$//g' )}"
        fatal "arg key defined multiple times [ ${f_yellow}${caught}${f_end} ]"
    fi

    if [[ $( getArgAttribute ${current_arg_def} "nargs_is_range" ) == 0 && ${it} == 1 ]]; then
    elif [[ $( getArgAttribute ${current_arg_def} "nargs_is_range" ) == 0 && ${it} != 1 ]]; then
        printBadNumArgs ${current_arg_def} ${it}
    elif [[ $( getArgAttribute ${current_arg_def} "nargs_has_top" ) == 0 ]]; then
    elif [[ $( getArgAttribute ${current_arg_def} "nargs_has_top" ) == 0 ]]; then
    elif [[ ${it} -ge $( getArgAttribute ${current_arg_def} "nargs_lower" ) && ${it} -le $( getArgAttribute ${current_arg_def} "nargs_upper" ) ]]; then
    else
        printBadNumArgs ${current_arg_def} ${it}
    fi

    choices=$( getArgAttribute ${current_arg_def} "choices" | tr ' ' '|' | sed -r 's/^\||\|$//g' )
    [[ -z ${choices} ]] && choices='.*' || choices="\b(${choices})\b"
    foreach term in ${(ps: :)current_args}; do
        [[ ! ${term} =~ ${choices} ]] && printBadArgChoice ${current_arg_def} ${choices} ${term}
    done

    args[$( getArgAttribute ${current_arg_def} "var_name" )]=${current_args}
}

function setArgs {
    [[ $@ =~ \-(h|\-help) ]] && printHelp
    local current_arg_def current_args it nargs
    current_arg_def=""; current_args=(); it=0; nargs=""
    while true; do
        [[ $1 =~ ^\\s*$ ]] && break

        if [[ ! ${current_arg_def} =~ ^\\s*$ && ${1} =~ ^- ]]; then
            setVar; current_arg_def=""; current_args=(); it=0; nargs=""
        fi

        if [[ ${1} =~ ^- ]]; then
            if [[ ${1} =~ ^-- ]]; then
                [[ $1 =~ ^--$ ]] && shift && break
                current_arg_def=$( echo ${arg_definitions} | grep -E "^[^;]*;${1[3,-1]}" )
                [[ ${current_arg_def} =~ ^\\s*$ ]] && fatal "undifined argument provided [ ${f_yellow}${1}${f_end} ]"
                nargs=$( getArgAttribute ${current_arg_def} "nargs" ); it=0
                if [[ ${nargs} =~ ^\\s*$ || ${nargs} == "0" ]]; then
                    setFlag ${current_arg_def}; current_arg_def=""; nargs=""
                fi
            else
                foreach term in ${(ps::)1[2,-2]}; do
                    arg_def=$( echo ${arg_definitions} | grep -E "^${term}" )
                    [[ ${arg_def} =~ ^\\s*$ ]] && fatal "undefined flag provided [ ${f_yellow}${term}${f_end} ]"
                    setFlag ${arg_def}
                done
                current_arg_def=$( echo ${arg_definitions} | grep -E "^${1[-1]}" )
                [[ ${current_arg_def} =~ ^\\s*$ ]] && fatal "undefined flag provided [ ${f_yellow}-${1[-1]}${f_end} ]"
                nargs=$( getArgAttribute ${current_arg_def} "nargs" ); it=0
                if [[ ${nargs} =~ ^\\s*$ || ${nargs} == "0" ]]; then
                    setFlag ${current_arg_def}; current_arg_def=""; nargs=""
                fi
            fi
        else
            [[ ${current_arg_def} =~ ^\\s*$ ]] && fatal "argument provided without key [ ${f_yellow}$1${f_end} ]"
            current_args+=$1; (( it = it + 1 ))
        fi
        shift 2> /dev/null; [[ ${status} != "0" ]] && break
    done
    [[ ! ${current_arg_def} =~ ^\\s*$ ]] && setVar
    [[ ${args[dump]} == 1 ]] && dumpArgs
}

function setDefaults {
    declare -rg req_init="__REQ__"
    foreach arg_def in ${(ps:\n:)arg_definitions}; do
        if [[ ! ${arg_def} =~ ^%% ]]; then
            local var_name=$( getArgAttribute ${arg_def} "var_name" )
            local  default=$( getArgAttribute ${arg_def} "default"  )
            local required=$( getArgAttribute ${arg_def} "required" )
            [[ ${required} == 1 ]] && default=${req_init}
            args[$var_name]=${default}
        fi
    done
}

function defineArgs {
    declare -Ag args

    # ? description and epilog print in help message only if defined
    declare -rg description=""
    declare -rg epilog=""

    # ? definitions above %% are arguments and below are flags
    # ? all arguments must have cli_word
    # ? choices are space separated (can be regex)

    # ! cli_char; cli_word; args_key; required; meta_var; nargs; options; default; help
    declare -rg arg_definitions=$( echo "
        %%
        Q;   quiet; ; ; ; ; ; 0; Quiet mode. No stdout.
        V; verbose; ; ; ; ; ; 0; Verbose mode. Extra stdout.
        D;    dump; ; ; ; ; ; 0; Dump argument/flag values and exit.
        h;    help; ; ; ; ; ; 0; Show this message and exit.
    " | sed    -r 's/^\s*//g;s/\s*;\s*/;/g' |
        sed -z -r 's/^\s*|\s*$//g;s/\n{2,}/\n/g' )

    declare -rg usage_str=$( genUsageStr ${arg_definitions} )
    declare -rg help_str=$( genHelpStr ${arg_definitions} )
}

function run {
    defineArgs; setDefaults; setArgs $@; validateArgs
    while [[ $# > 0 ]]; do [[ $1 == "--" ]] && shift && break; shift; done
    quietMode timeFunc main $@
}

function testVPN {
    info "\n${f_bold}${f_dark_blue}TESTING WIREGUARD${f_end}"

    info "${f_purple}add config w/o auto start${f_end}"
    curl -X POST "localhost:8001/vpn/add?config=client"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''

    info "${f_purple}start vpn${f_end}"
    curl -X POST "localhost:8001/vpn/start?config=client"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''

    info "${f_purple}stop vpn${f_end}"
    curl -X POST "localhost:8001/vpn/stop?config=client"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''

    info "${f_purple}remove config after stop${f_end}"
    curl -X POST "localhost:8001/vpn/remove?config=client"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''

    info "${f_purple}add config w/ auto start${f_end}"
    curl -X POST "localhost:8001/vpn/add?config=client&autostart=true"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''

    info "${f_purple}remove config w/o stop${f_end}"
    curl -X POST "localhost:8001/vpn/remove?config=client"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''
}

function testRclone {
    info "\n${f_bold}${f_dark_blue}TESTING RCLONE${f_end}"

    info "${f_green}start server${f_end}"
    curl -X POST "localhost:8001/vpn/add?config=client&autostart=true"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''

    info "${f_purple}add remote w/o auto mount${f_end}"
    curl -X POST "localhost:8001/rclone/add?remote_name=sgnas&mount_path=$HOME/sg_nas"; echo ''
    curl -X GET  "localhost:8001/rclone/status"; echo ''

    # sleep 5

    info "${f_purple}mount remote${f_end}"
    curl -X POST "localhost:8001/rclone/mount?remote_name=sgnas"; echo ''
    curl -X GET  "localhost:8001/rclone/status"; echo ''

    info "${f_purple}unmount remote${f_end}"
    curl -X POST "localhost:8001/rclone/unmount?remote_name=sgnas"; echo ''
    curl -X GET  "localhost:8001/rclone/status"; echo ''

    info "${f_purple}remove remote after unmount${f_end}"
    curl -X POST "localhost:8001/rclone/remove?remote_name=sgnas"; echo ''
    curl -X GET  "localhost:8001/rclone/status"; echo ''

    info "${f_purple}add remote w/ auto mount${f_end}"
    curl -X POST "localhost:8001/rclone/add?remote_name=sgnas&mount_path=$HOME/sg_nas&automount=true"; echo ''
    curl -X GET  "localhost:8001/rclone/status"; echo ''

    info "${f_purple}remove remote w/o unmount${f_end}"
    curl -X POST "localhost:8001/rclone/remove?remote_name=sgnas"; echo ''
    curl -X GET  "localhost:8001/rclone/status"; echo ''

    info "${f_green}stop server${f_end}"
    curl -X POST "localhost:8001/vpn/remove?config=client"; echo ''
    curl -X GET  "localhost:8001/vpn/status"; echo ''
}

function main {
    testVPN
    testRclone
}

run $@
