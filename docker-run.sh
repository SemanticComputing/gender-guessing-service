#!/usr/bin/env bash

#################################################
# GENERAL CMD ARGS AND DEBUGGING. DO NOT CHANGE #
#################################################
set -euo pipefail
D="$(readlink -f "$(dirname "$0")")"
while [ $# -gt 0 ] && [[ $1 =~ ^-.* ]]; do
    case $1 in
        --help|-h) OPT_HELP=1; shift;;
        --debug) set -x; shift;;
        --sh) OPT_SHELL=1; shift;;
        --bash) OPT_BASH=1; shift;;
        -*) shift;;
    esac
done



###################################
# OPTIONS FOR DOCKER. CHANG THESE #
###################################

# Variables
IMAGE="gender-guessing-service"
CONTAINER_NAME="$IMAGE"
IP="172.30.20.65"
CONTAINER_PORTS[1]="5000"
HOST_PORTS[1]="5000"
NETWORK="seco"
NETWORK_CIDR="172.30.20.0/22"
CONTAINER_USER="$UID"
#DOCKER_ENV_FILE="docker.env"



###############################
# COMMON STUFF. DO NOT CHANGE #
###############################

usage() {
    echo "$0 --debug [--sh|--bash] [OTHER ARGS...]"
    exit 1
}

info() {
    echo "$1"
}

info_aligned() {
    local FORMAT=""
    local W="$1"
    shift
    for i in $(seq 1 $#); do
        FORMAT+="%-${W}s"
    done
    printf "$FORMAT\n" "$@"
}

[ -n "${OPT_HELP-}" ] && usage

# Print some info
[ -v IMAGE ]            && info_aligned 18 "IMAGE:" "$IMAGE"
[ -v CONTAINER_NAME ]   && info_aligned 18 "CONTAINER NAME:" "$CONTAINER_NAME"
[ -v CONTAINER_USER ]   && info_aligned 18 "CONTAINER USER:" "$CONTAINER_USER"
[ -v NETWORK ]          && info_aligned 18 "DOCKER NETWORK:" "$NETWORK"
[ -v IP ]               && info_aligned 18 "IP:" "$IP"
for i in "${!CONTAINER_PORTS[@]}"; do
    info_aligned 18 "EXPOSED:" "${CONTAINER_PORTS[$i]} -> ${HOST_PORTS[$i]}"
done
[ -v DOCKER_ENV_FILE ]  && info_aligned 18 "ENVIRONMENT FILE:" "$DOCKER_ENV_FILE"
for i in "${!VOLUME_TARGETS[@]}"; do
    info_aligned 18 "MOUNT:" "${VOLUME_SOURCES[$i]} -> ${VOLUME_TARGETS[$i]}"
done
echo ""

# Create volume source dirs if not exist
for i in "${!VOLUME_TARGETS[@]}"; do
    [ -z "${VOLUME_TARGETS[$i]}" ] || [ -e "${VOLUME_SOURCES[$i]}" ] || mkdir -p "${VOLUME_SOURCES[$i]}"
done

# Create docker network if it does not exist
[ -z "$NETWORK" ] || docker network inspect "$NETWORK" > /dev/null 2>&1 || docker network create --subnet $NETWORK_CIDR $NETWORK;

# Run the container
DOCKER_CMD=
DOCKER_CMD="docker run -it --rm"
DOCKER_CMD+=${CONTAINER_NAME:+' --name "$CONTAINER_NAME"'}
DOCKER_CMD+=${CONTAINER_USER:+' -u "$CONTAINER_USER"'}
DOCKER_CMD+=${NETWORK:+' --network "$NETWORK"'}
DOCKER_CMD+=${IP:+' --ip "$IP"'}
for i in ${!CONTAINER_PORTS[@]}; do
    DOCKER_CMD+="$(printf ' --publish %q:%q' "${HOST_PORTS[$i]}" "${CONTAINER_PORTS[$i]}")"
    DOCKER_CMD+="$(printf ' --expose %q' "${CONTAINER_PORTS[$i]}")"
done
DOCKER_CMD+=${DOCKER_ENV_FILE:+' --env-file="$DOCKER_ENV_FILE"'}
for i in ${!VOLUME_TARGETS[@]}; do
    DOCKER_CMD+="$(printf ' --mount type=bind,source=%q,target=%q' "${VOLUME_SOURCES[$i]}" "${VOLUME_TARGETS[$i]}")"
done
[ -n "${OPT_SHELL-}" ] && DOCKER_CMD+=" --entrypoint /bin/sh"
[ -n "${OPT_BASH-}" ] && DOCKER_CMD+=" --entrypoint /bin/bash"
DOCKER_CMD+=' $IMAGE'

eval "$DOCKER_CMD"
{ set +x; } 2> /dev/null
