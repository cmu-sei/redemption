
CI_PROJECT_DIR := $(if $(CI_PROJECT_DIR),$(CI_PROJECT_DIR),${PWD})
# ${REDEMPTION_IMAGE} must contain the name of the Redemption Docker image


all:	build test

build:
	@echo "Compiling with GCC"
	gcc -c -g3 -Wall  src/*.c


test:	sa

sa:	cppcheck.xml

rosecheckers.txt:
	@echo "Running Rosecheckers"
	docker run --rm -v ${CI_PROJECT_DIR}/src:/src  ghcr.io/cmu-sei/cert-rosecheckers/rosebud:latest  bash -c 'rosecheckers  /src/toy.c' 2>&1 | fgrep -v .h | tee $@

cppcheck.xml:
	@echo "Running cppcheck"
	docker run --security-opt label=disable --rm -v ${CI_PROJECT_DIR}/src:/src facthunder/cppcheck:latest cppcheck -v --enable="all" --language="c" --force --xml . 2> $@

clang-tidy.txt:
	@echo "Running clang-tidy"
	docker run --rm -v ${CI_PROJECT_DIR}:/data -w /data/src  silkeh/clang  bash -c "clang-tidy -checks='*' *.c" > $@


deploy:	publish repair

publish:
	@echo "Publishing"
	-mkdir distrib
	cd src ; tar czf ../distrib/toy.tgz * ; cd ..

alerts.json:	sa
	docker run --rm  -v ${CI_PROJECT_DIR}:/data -w /data  ${REDEMPTION_IMAGE}  python3 /host/code/analysis/alerts2input.py  src  cppcheck_oss  cppcheck.xml  alerts.json
#[NOTE] --alerts isn't used here. Only path of /data/alerts.json, which conflicts with the documentation in /redemption/doc/examples/simple/README.MD in Execution
repair:	alerts.json
	@echo "Repairing"
	docker run --rm  -v ${CI_PROJECT_DIR}:/data -w /host/code/acr  ${REDEMPTION_IMAGE}   python3 end_to_end_acr.py  /data/src/test_errors.c  autogen  /data/alerts.json  --in-place  --base-dir /data/src --repair-includes true
	/bin/sh -f ./CI/create-pull-request.sh


clean:
	@echo "Cleaning"
	-rm -rf *.o rosecheckers.txt clang-tidy.txt cppcheck.xml alerts.json out distrib
