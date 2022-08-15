if [[ ! $PWD =~ VENV_ ]]; then
  echo "Invalid travis environment!"
  exit 1
fi
if [[ -z $TRAVIS_BUILD_DIR && $PWD =~ /build/ ]]; then
  [[ $(basename $PWD) == "tests" ]] && TRAVIS_BUILD_DIR=$(readlink -f ./..) || TRAVIS_BUILD_DIR=$(readlink -f ./)
  export TRAVIS_BUILD_DIR
  echo "\$ export TRAVIS_BUILD_DIR=\"$TRAVIS_BUILD_DIR\""
fi

if [ "${BASH_SOURCE-}" == "$0" ]; then
    echo "Use:"
    echo ". $0"
fi
