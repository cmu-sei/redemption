
CI_PROJECT_DIR := $(if $(CI_PROJECT_DIR),$(CI_PROJECT_DIR),${PWD})
# ${REDEMPTION_IMAGE} must contain the name of the Redemption Docker image


all:	build test

build:	publish compile_commands.json

publish:
	@echo "Publishing"
	-mkdir distrib
	cd src ; tar czf ../distrib/dos2unix.tgz * ; cd ..

compile_commands.json:
	@echo "Compiling with Clang"
	@if [ ! -f src/Makefile ]; then echo "There should be a src/Makefile to build the codebase"; fi
	docker run --rm  -v ${CI_PROJECT_DIR}:/data -w /data -w /data/src  ${REDEMPTION_IMAGE}  bear -- make CC=clang
	mv src/compile_commands.json .


test:	sa

sa:	clang-tidy.txt

rosecheckers.txt:
	@echo "Running Rosecheckers"
	docker run --rm -v ${CI_PROJECT_DIR}/src:/src  ghcr.io/cmu-sei/cert-rosecheckers/rosebud:latest  bash -c 'rosecheckers  /src/toy.c' 2>&1 | fgrep -v .h | tee $@

cppcheck.xml:	compile_commands.json
	@echo "Running cppcheck"
	cp compile_commands.json src
	docker run --security-opt label=disable --rm -v ${CI_PROJECT_DIR}/src:/src facthunder/cppcheck:latest cppcheck -v --enable="all" --language="c" --force --xml . 2> $@

clang-tidy.txt:	compile_commands.json
	@echo "Running clang-tidy"
	cp compile_commands.json src
	docker run --rm -v ${CI_PROJECT_DIR}:/data -w /data/src  silkeh/clang  bash -c "clang-tidy -checks='*' *.c" > $@


deploy:	publish deploy_repair

alerts.json:
	docker run --rm  -v ${CI_PROJECT_DIR}:/data -w /data  ${REDEMPTION_IMAGE}  python3 /host/code/analysis/alerts2input.py  src  clang_tidy_oss  clang-tidy.txt  alerts.json

repair:	alerts.json
	@echo "Repairing"
	docker run --rm  -v ${CI_PROJECT_DIR}:/data -w /host/code/acr  ${REDEMPTION_IMAGE}   python3  sup.py  -c /data/compile_commands.json  -a /data/alerts.json  -b /data/src  --repaired-src /data/src

deploy_repair:	repair
	make clean
	# Clean required so Git knows what new files can be added, if any
	@echo "Deploying repair"
	/bin/sh -f ./CI/create-pull-request.sh


src-clean:
	@echo "Cleaning source"
	cd src ; make clean ; cd ..
	git checkout src/man/*/*.1 src/man/*/*.htm src/man/*/*/*.1 src/man/*/*/*.htm src/po/dos2unix.pot

clean:	src-clean
	@echo "Cleaning"
	-rm -rf rosecheckers.txt clang-tidy.txt cppcheck.xml alerts.json out
	-rm -rf compile_commands.json src/compile_commands.json distrib
