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
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/wrk.9ea3194ec8a620780e895031.raw.stderr.txt | gzip > $ast_out_dir/wrk.9ea3194ec8a620780e895031.raw.ast.json.gz; echo $? > $ast_out_dir/wrk.9ea3194ec8a620780e895031.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/wrk.9ea3194ec8a620780e895031.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/net.eea18351108434e5fbc24b65.raw.stderr.txt | gzip > $ast_out_dir/net.eea18351108434e5fbc24b65.raw.ast.json.gz; echo $? > $ast_out_dir/net.eea18351108434e5fbc24b65.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/net.eea18351108434e5fbc24b65.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ssl.377f4aff3e42137dba1ada59.raw.stderr.txt | gzip > $ast_out_dir/ssl.377f4aff3e42137dba1ada59.raw.ast.json.gz; echo $? > $ast_out_dir/ssl.377f4aff3e42137dba1ada59.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ssl.377f4aff3e42137dba1ada59.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/aprintf.a4fecd9fcca4e37664c4d566.raw.stderr.txt | gzip > $ast_out_dir/aprintf.a4fecd9fcca4e37664c4d566.raw.ast.json.gz; echo $? > $ast_out_dir/aprintf.a4fecd9fcca4e37664c4d566.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/aprintf.a4fecd9fcca4e37664c4d566.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/stats.54bd3f48f35e2ca444f6b20c.raw.stderr.txt | gzip > $ast_out_dir/stats.54bd3f48f35e2ca444f6b20c.raw.ast.json.gz; echo $? > $ast_out_dir/stats.54bd3f48f35e2ca444f6b20c.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/stats.54bd3f48f35e2ca444f6b20c.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/script.d6d28b9e892039c23a4faeb4.raw.stderr.txt | gzip > $ast_out_dir/script.d6d28b9e892039c23a4faeb4.raw.ast.json.gz; echo $? > $ast_out_dir/script.d6d28b9e892039c23a4faeb4.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/script.d6d28b9e892039c23a4faeb4.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/units.f8d8aaaf99b48d078a513b8e.raw.stderr.txt | gzip > $ast_out_dir/units.f8d8aaaf99b48d078a513b8e.raw.ast.json.gz; echo $? > $ast_out_dir/units.f8d8aaaf99b48d078a513b8e.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/units.f8d8aaaf99b48d078a513b8e.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ae.7ee415ec97e4cf45b24a402d.raw.stderr.txt | gzip > $ast_out_dir/ae.7ee415ec97e4cf45b24a402d.raw.ast.json.gz; echo $? > $ast_out_dir/ae.7ee415ec97e4cf45b24a402d.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ae.7ee415ec97e4cf45b24a402d.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/zmalloc.41fe986627075c32597d5ef5.raw.stderr.txt | gzip > $ast_out_dir/zmalloc.41fe986627075c32597d5ef5.raw.ast.json.gz; echo $? > $ast_out_dir/zmalloc.41fe986627075c32597d5ef5.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/zmalloc.41fe986627075c32597d5ef5.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/http_parser.150a7c7d23cd201eb810df70.raw.stderr.txt | gzip > $ast_out_dir/http_parser.150a7c7d23cd201eb810df70.raw.ast.json.gz; echo $? > $ast_out_dir/http_parser.150a7c7d23cd201eb810df70.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/http_parser.150a7c7d23cd201eb810df70.raw.ll
cd /separate_build/wrk
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/bytecode.962c05fb9415f5cf973fca32.raw.stderr.txt | gzip > $ast_out_dir/bytecode.962c05fb9415f5cf973fca32.raw.ast.json.gz; echo $? > $ast_out_dir/bytecode.962c05fb9415f5cf973fca32.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/bytecode.962c05fb9415f5cf973fca32.raw.ll
