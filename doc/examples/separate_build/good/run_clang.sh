#!/bin/sh

ast_out_dir=$1

if [ "$#" -ne 1 ]; then
    echo "Usage $0 ast_out_dir"
    exit 1
fi
if [ ! -d "$ast_out_dir" ]; then
    echo "Error: Output directory ($ast_out_dir) does not exist!"
    exit 1
fi
ast_out_dir=`realpath $ast_out_dir`
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/wrk.ec56feab018de68d03c6c726.raw.stderr.txt | gzip > $ast_out_dir/wrk.ec56feab018de68d03c6c726.raw.ast.json.gz; echo $? > $ast_out_dir/wrk.ec56feab018de68d03c6c726.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/wrk.ec56feab018de68d03c6c726.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/net.ac6f98a4e01366f160bd9196.raw.stderr.txt | gzip > $ast_out_dir/net.ac6f98a4e01366f160bd9196.raw.ast.json.gz; echo $? > $ast_out_dir/net.ac6f98a4e01366f160bd9196.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/net.ac6f98a4e01366f160bd9196.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ssl.e277fcb15b9feb90822c5b7b.raw.stderr.txt | gzip > $ast_out_dir/ssl.e277fcb15b9feb90822c5b7b.raw.ast.json.gz; echo $? > $ast_out_dir/ssl.e277fcb15b9feb90822c5b7b.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ssl.e277fcb15b9feb90822c5b7b.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/aprintf.16e23ddc8bc6a21bbbd19127.raw.stderr.txt | gzip > $ast_out_dir/aprintf.16e23ddc8bc6a21bbbd19127.raw.ast.json.gz; echo $? > $ast_out_dir/aprintf.16e23ddc8bc6a21bbbd19127.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/aprintf.16e23ddc8bc6a21bbbd19127.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/stats.80ae148837c0a654b4c83ab7.raw.stderr.txt | gzip > $ast_out_dir/stats.80ae148837c0a654b4c83ab7.raw.ast.json.gz; echo $? > $ast_out_dir/stats.80ae148837c0a654b4c83ab7.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/stats.80ae148837c0a654b4c83ab7.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/script.216a9235fbf7d9ea49ea859f.raw.stderr.txt | gzip > $ast_out_dir/script.216a9235fbf7d9ea49ea859f.raw.ast.json.gz; echo $? > $ast_out_dir/script.216a9235fbf7d9ea49ea859f.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/script.216a9235fbf7d9ea49ea859f.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/units.4a5c6e70bde4e33b61874d32.raw.stderr.txt | gzip > $ast_out_dir/units.4a5c6e70bde4e33b61874d32.raw.ast.json.gz; echo $? > $ast_out_dir/units.4a5c6e70bde4e33b61874d32.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/units.4a5c6e70bde4e33b61874d32.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ae.89db0001e30b382a980979cd.raw.stderr.txt | gzip > $ast_out_dir/ae.89db0001e30b382a980979cd.raw.ast.json.gz; echo $? > $ast_out_dir/ae.89db0001e30b382a980979cd.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ae.89db0001e30b382a980979cd.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/zmalloc.3dc24cbde3b17addb65105dc.raw.stderr.txt | gzip > $ast_out_dir/zmalloc.3dc24cbde3b17addb65105dc.raw.ast.json.gz; echo $? > $ast_out_dir/zmalloc.3dc24cbde3b17addb65105dc.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/zmalloc.3dc24cbde3b17addb65105dc.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/http_parser.820c829af790cf195720decc.raw.stderr.txt | gzip > $ast_out_dir/http_parser.820c829af790cf195720decc.raw.ast.json.gz; echo $? > $ast_out_dir/http_parser.820c829af790cf195720decc.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/http_parser.820c829af790cf195720decc.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/bytecode.4bebae1122355cb814a16ca7.raw.stderr.txt | gzip > $ast_out_dir/bytecode.4bebae1122355cb814a16ca7.raw.ast.json.gz; echo $? > $ast_out_dir/bytecode.4bebae1122355cb814a16ca7.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/bytecode.4bebae1122355cb814a16ca7.raw.ll
