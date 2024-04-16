#!/bin/sh

# Script to notify Azure-Gitlab of new repairs

if git status --porcelain | grep "^ M src/"; then
    CURRENT_BRANCH=$CI_COMMIT_REF_NAME
    if [ -z "${CURRENT_BRANCH}" ]; then
        CURRENT_BRANCH=$(git branch --show-current)
    fi

    PREFIX="temp_"
    case "${CURRENT_BRANCH}" in
        ${PREFIX}*)  echo "Code already repaired" ; exit 1 ;;
        *)  echo "Creating pull request" ;;
    esac

    # Login id of the user that placed initial commit (if available)
    USER_NAME=${GITLAB_USER_LOGIN}
    if [ -z "${USER_NAME}" ]; then
        USER_NAME=${USER}
    fi

    TEMP_BRANCH=${PREFIX}$(date +%y-%m-%d-%H-%M-%S)
    # Read from Gitlab environment
    URL=${CODEBASE_URL}
    # Read from Gitlab environment
    TOKEN=${REDEMPTION_TOKEN}

    echo "Current branch: " "${CURRENT_BRANCH}"
    echo "New branch: " "${TEMP_BRANCH}"
    echo "user name: " "${USER_NAME}"

    git checkout -b "${TEMP_BRANCH}"
    git add -A src/*
    git commit -m "redemption output"
    git remote add origin4  "https://${USER_NAME}:${TOKEN}@${URL}"
    git push --set-upstream origin4  "${TEMP_BRANCH}"  \
        -o merge_request.create  \
        -o merge_request.target="${CURRENT_BRANCH}"  \
        -o merge_request.remove_source_branch  \
        -o merge_request.assign="${USER_NAME}" \
        -o merge_request.title="Suggested Repairs"

else
    echo No repairs
fi
