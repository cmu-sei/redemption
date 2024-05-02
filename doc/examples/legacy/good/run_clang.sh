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
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/wrk.5c12e5e6976a81bda18922c1.raw.stderr.txt | gzip > $ast_out_dir/wrk.5c12e5e6976a81bda18922c1.raw.ast.json.gz; echo $? > $ast_out_dir/wrk.5c12e5e6976a81bda18922c1.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/wrk.5c12e5e6976a81bda18922c1.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/net.ffd1b0d3ac8b1c7296add08c.raw.stderr.txt | gzip > $ast_out_dir/net.ffd1b0d3ac8b1c7296add08c.raw.ast.json.gz; echo $? > $ast_out_dir/net.ffd1b0d3ac8b1c7296add08c.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/net.ffd1b0d3ac8b1c7296add08c.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ssl.0a42031453cfa34b8cb8a25f.raw.stderr.txt | gzip > $ast_out_dir/ssl.0a42031453cfa34b8cb8a25f.raw.ast.json.gz; echo $? > $ast_out_dir/ssl.0a42031453cfa34b8cb8a25f.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ssl.0a42031453cfa34b8cb8a25f.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/aprintf.251226a0b4d10ad3ad2059fc.raw.stderr.txt | gzip > $ast_out_dir/aprintf.251226a0b4d10ad3ad2059fc.raw.ast.json.gz; echo $? > $ast_out_dir/aprintf.251226a0b4d10ad3ad2059fc.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/aprintf.251226a0b4d10ad3ad2059fc.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/stats.6f14fc69770b6cdd3b88ec58.raw.stderr.txt | gzip > $ast_out_dir/stats.6f14fc69770b6cdd3b88ec58.raw.ast.json.gz; echo $? > $ast_out_dir/stats.6f14fc69770b6cdd3b88ec58.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/stats.6f14fc69770b6cdd3b88ec58.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/script.efc9a0b2e86333aefd9962be.raw.stderr.txt | gzip > $ast_out_dir/script.efc9a0b2e86333aefd9962be.raw.ast.json.gz; echo $? > $ast_out_dir/script.efc9a0b2e86333aefd9962be.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/script.efc9a0b2e86333aefd9962be.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/units.75866747cfc84730e6ff84eb.raw.stderr.txt | gzip > $ast_out_dir/units.75866747cfc84730e6ff84eb.raw.ast.json.gz; echo $? > $ast_out_dir/units.75866747cfc84730e6ff84eb.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/units.75866747cfc84730e6ff84eb.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ae.47a0cd446f5950f7b89e9fe4.raw.stderr.txt | gzip > $ast_out_dir/ae.47a0cd446f5950f7b89e9fe4.raw.ast.json.gz; echo $? > $ast_out_dir/ae.47a0cd446f5950f7b89e9fe4.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ae.47a0cd446f5950f7b89e9fe4.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/zmalloc.ed9a8e3680c1b18dbd07e371.raw.stderr.txt | gzip > $ast_out_dir/zmalloc.ed9a8e3680c1b18dbd07e371.raw.ast.json.gz; echo $? > $ast_out_dir/zmalloc.ed9a8e3680c1b18dbd07e371.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/zmalloc.ed9a8e3680c1b18dbd07e371.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/http_parser.445f867a16ce1c82ee80775d.raw.stderr.txt | gzip > $ast_out_dir/http_parser.445f867a16ce1c82ee80775d.raw.ast.json.gz; echo $? > $ast_out_dir/http_parser.445f867a16ce1c82ee80775d.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/http_parser.445f867a16ce1c82ee80775d.raw.ll
cd /legacy/wrk-4.2.0
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/bytecode.c4fa185d4064339cee21bb0a.raw.stderr.txt | gzip > $ast_out_dir/bytecode.c4fa185d4064339cee21bb0a.raw.ast.json.gz; echo $? > $ast_out_dir/bytecode.c4fa185d4064339cee21bb0a.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/bytecode.c4fa185d4064339cee21bb0a.raw.ll
