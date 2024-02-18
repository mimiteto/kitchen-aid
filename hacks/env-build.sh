#! /usr/bin/env bash

# Builds environment for the dev deployment of our project.

APP_NAME="${kitchen-aid}"
IMAGE_REPO="${APP_NAME}:latest"
CLUSTER_NAME="${APP_NAME}"
CONTEXT_NAME="kind-${CLUSTER_NAME}"
RESOURCES_DIR="resources/deployment"

function exit_with_error() {
        case "${1}" in
                "dependencies")
                        echo "${2}"
                        exit 1
                        ;;
                "conf")
                        echo "${2}"
                        exit 2
                        ;;
                *)
                        echo "Unknown error"
                        echo "${1}: ${2}"
                        exit 3
                        ;;
        esac
}

function kind_run_cluster() {
        if [ "$(kubectl config current-context 2>/dev/null)" != "${CONTEXT_NAME}" ]; then
                kind create cluster --config hacks/.env-build/kind-config.yaml
        fi
}

function run_cluster() {
        if ! which kind; then
                exit_with_error "dependencies" "No suported cluster tool found. Please install kind or k3d."
        fi
        kind_run_cluster
        while [ "$(kubectl get pods -A --no-headers | grep -c -v -e Running -e Complete)" -gt "0" ]; do
                sleep 1
        done
}

function kind_import_images() {
        kind load docker-image "${1}" --name "${CLUSTER_NAME}"
}

function import_images() {
        if ! which yq; then
                exit_with_error "dependencies" "Can't read image version (yq nopt found)"
        fi
        img_version="$(yq -r .appVersion deploy/kitchen-aid/Chart.yaml)"
        if which kind; then
                kind_import_images "${IMAGE_REPO}:${img_version}"
        else
                exit_with_error "dependencies" "Can't load images (no supported cluser tool found)"
        fi
}

function clear_cluster() {
        if which kind; then
                kind delete cluster --name "${CLUSTER_NAME}"
        else
                exit_with_error "dependencies" "Can't clear cluster (no supported cluser tool found)"
        fi
}

# Read first line from file, strip the "# exec:" part and execute it
# Commands are executed within the same dir as the file
function deplloy_file() {
        local file="${1}"
        if [ -f "${file}" ]; then
                cmd="$(head -n 1 "${file}" | sed -e 's/# exec: //')"
                dir="$(dirname "${file}")"
                (cd "${dir}" && ${cmd})
        fi
}

# Recursivelly deploy all resources in a directory and subdirs
# First we will deploy files within a dir
# Then we will deploy subdirs
function deploy_resources() {
        local res_dir="${1}"

        # Deploy files in the dir
        for file in "${res_dir}"/*; do
                if [ -f "${file}" ]; then
                        deploy_file "${file}"
                fi
        done
        # Deploy subdirs
        for subdir in "${res_dir}"/*; do
                if [ -d "${subdir}" ]; then
                        deploy_resources "${subdir}"
                fi
        done
}

function deploy_dependencies() {
        if ! which helm; then
                exit_with_error "dependencies" "Helm not found. Please install it."
        fi
        if ! which kubectl; then
                exit_with_error "dependencies" "Kubectl not found. Please install it."
        fi
        if ! which yq; then
                exit_with_error "dependencies" "yq not found. Please install it."
        fi
        deploy_resources "${RESOURCES_DIR}"
}

function main() {
        if [ "${1}" == "--clear" ]; then
                # shellcheck disable=SC2119
                clear_cluster "${CLUSTER_NAME}"
                exit 0
        fi
        check_conf
        run_cluster
        import_images
        deploy_dependencies
}

main "${@}"
