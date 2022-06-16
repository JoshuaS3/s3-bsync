#!/usr/bin/env bash

# Script variables
PYTHON_MAJOR=3
PYTHON_MINOR=7
ACCEPTABLE_PYTHON_COMMANDS="python3 python3.10 python3.9 python3.8 python3.7 python"

SCRIPT_SOURCE_DIR=$(dirname -- "${BASH_SOURCE[0]}")

while read -r requirement
do
    REQUIRED_PIP_MODULES="$REQUIRED_PIP_MODULES $(sed -r "s/:.*//g" <<< $requirement)"
    REQUIRED_PYTHON_MODULES="$REQUIRED_PYTHON_MODULES $(sed -r "s/.*://g" <<< $requirement)"
done < $SCRIPT_SOURCE_DIR/requirements.txt

# Plumbing
set -o pipefail

RESTORE=$(echo -en '\033[0m')
STANDOUT=$(echo -en '\033[7m')
RED=$(echo -en '\033[00;31m')
GREEN=$(echo -en '\033[00;32m')
YELLOW=$(echo -en '\033[00;33m')
PURPLE=$(echo -en '\033[00;35m')
LIGHTGRAY=$(echo -en '\033[00;37m')
LRED=$(echo -en '\033[01;31m')
LYELLOW=$(echo -en '\033[01;33m')
LBLUE=$(echo -en '\033[01;34m')
LCYAN=$(echo -en '\033[01;36m')



# Handle argument input
case $1 in
    h|help|?|-h|-help|-?|--h|--help|--?)
        echo "Usage: ./install.sh [install|uninstall] [<python executable>]"
        exit 0
        ;;
    install)
        PYTHON_COMMAND=$2
        ;;
    uninstall)
        UNINSTALL=1
        PYTHON_COMMAND=$2
        ;;
    *)
        PYTHON_COMMAND=$1
        ;;
esac


# Report operating mode
if [ -z $UNINSTALL ]; then
    echo "${YELLOW}Running in ${LYELLOW}INSTALL${YELLOW} mode${RESTORE}"
else
    echo "${YELLOW}Running in ${LYELLOW}UNINSTALL${YELLOW} mode${RESTORE}"
    REQUIRED_PIP_MODULES="pip"
    REQUIRED_PYTHON_MODULES="pip"
fi


# Determine Python interpreter to use
echo "${LIGHTGRAY}Determining Python interpreter${RESTORE}"
if [ -z $PYTHON_COMMAND ]; then
    for COMMAND in $ACCEPTABLE_PYTHON_COMMANDS
    do
        if command -v $COMMAND &> /dev/null; then
            PYTHON_COMMAND=$COMMAND
            break
        fi
    done
fi

# Expand interpreter command, verify with `import sys` test instruction
PYTHON_COMMAND=$(command -v $PYTHON_COMMAND)
if [ -z $PYTHON_COMMAND ]; then
    echo "  ${RED}Python interpreter not found${RESTORE}"
    exit 1
fi
if [ -h "$PYTHON_COMMAND" ]; then
    PYTHON_COMMAND=$(readlink -f $PYTHON_COMMAND)
fi
echo "  Trying interpreter [ ${LYELLOW}$PYTHON_COMMAND${RESTORE} ]"
if ! $PYTHON_COMMAND -c "import sys"; then
    echo "  ${RED}Executable is not Python${RESTORE}"
    exit 1
fi


# Verifying Python version
echo "${LIGHTGRAY}Checking Python version${RESTORE} [ needs ${LIGHTGRAY}>=$PYTHON_MAJOR.$PYTHON_MINOR${RESTORE} ]"
PYTHON_VERSION_STRING=$($PYTHON_COMMAND -c "print('.'.join([str(a) for a in __import__('sys').version_info[:3]]))")
if ! $PYTHON_COMMAND -c "import sys;exit(not(sys.version_info.major==$PYTHON_MAJOR and sys.version_info.minor>=$PYTHON_MINOR))"; then
    echo "  ${RED}Python version must be ${RESTORE}[ ${LCYAN}>=$PYTHON_MAJOR.$PYTHON_MINOR${RESTORE} ]${RED}."\
                 "Installed is ${RESTORE}[ ${LCYAN}$PYTHON_VERSION_STRING${RESTORE} ]"
    exit 1
fi
echo "  Version [ ${LCYAN}$PYTHON_VERSION_STRING${RESTORE} ] acceptable"


# Verifying required modules are installed
echo "${LIGHTGRAY}Checking Python modules installed${RESTORE}"
for MODULE in $(seq 1 $(wc -w <<< $REQUIRED_PIP_MODULES))
do
    PIP_MODULE=$(awk -v N=$MODULE '{print $N}' <<< "$REQUIRED_PIP_MODULES")
    PYTHON_MODULE=$(awk -v N=$MODULE '{print $N}' <<< "$REQUIRED_PYTHON_MODULES")
    if ! $PYTHON_COMMAND -c "import $PYTHON_MODULE" &> /dev/null; then
        echo "  ${RED}Required Python module ${RESTORE}[ ${LBLUE}$PYTHON_MODULE${RESTORE} ] ${RED}not found${RESTORE}"
        echo "  Install with ${PURPLE}$PYTHON_COMMAND -m pip install $PIP_MODULE${RESTORE}"
        exit 1
    fi
    echo "  Module [ ${LBLUE}$PYTHON_MODULE${RESTORE} ] found"
done
echo "  ${GREEN}All required modules found${RESTORE}"


# Set pip command based on script mode
if [ -z $UNINSTALL ]; then
    PIP_COMMAND="$PYTHON_COMMAND -m pip install $SCRIPT_SOURCE_DIR/"
else
    PIP_COMMAND="$PYTHON_COMMAND -m pip uninstall --yes s3-bsync"
fi


# Run pip command and handle output
function indent() {
    sed 's/^/  /';
}
echo "${LIGHTGRAY}Running [ ${PURPLE}$PIP_COMMAND${LIGHTGRAY} ]${RESTORE}"
if $PIP_COMMAND 2>&1 | indent; then
    echo "${GREEN}Success${RESTORE}"
    exit 0
else
    ERROR_CODE=$?
    echo "${LRED}${STANDOUT}pip did not exit successfully (status code $ERROR_CODE)${RESTORE}"
    exit $ERROR_CODE
fi
