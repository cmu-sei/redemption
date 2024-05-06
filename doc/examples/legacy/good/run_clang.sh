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
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/wrk.6199cfeb0629afcfd968f7e0.raw.stderr.txt | gzip > $ast_out_dir/wrk.6199cfeb0629afcfd968f7e0.raw.ast.json.gz; echo $? > $ast_out_dir/wrk.6199cfeb0629afcfd968f7e0.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/wrk.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/wrk.6199cfeb0629afcfd968f7e0.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/net.5f1e22e17d0bb67441060a47.raw.stderr.txt | gzip > $ast_out_dir/net.5f1e22e17d0bb67441060a47.raw.ast.json.gz; echo $? > $ast_out_dir/net.5f1e22e17d0bb67441060a47.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/net.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/net.5f1e22e17d0bb67441060a47.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ssl.71f3dc71318bba8b79451f4f.raw.stderr.txt | gzip > $ast_out_dir/ssl.71f3dc71318bba8b79451f4f.raw.ast.json.gz; echo $? > $ast_out_dir/ssl.71f3dc71318bba8b79451f4f.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ssl.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ssl.71f3dc71318bba8b79451f4f.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/aprintf.0b09d3e0ee28465c7f34faf1.raw.stderr.txt | gzip > $ast_out_dir/aprintf.0b09d3e0ee28465c7f34faf1.raw.ast.json.gz; echo $? > $ast_out_dir/aprintf.0b09d3e0ee28465c7f34faf1.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/aprintf.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/aprintf.0b09d3e0ee28465c7f34faf1.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/stats.ae1ac2129331a8934eb79285.raw.stderr.txt | gzip > $ast_out_dir/stats.ae1ac2129331a8934eb79285.raw.ast.json.gz; echo $? > $ast_out_dir/stats.ae1ac2129331a8934eb79285.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/stats.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/stats.ae1ac2129331a8934eb79285.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/script.8abdc67a2dffc56dfe3411ab.raw.stderr.txt | gzip > $ast_out_dir/script.8abdc67a2dffc56dfe3411ab.raw.ast.json.gz; echo $? > $ast_out_dir/script.8abdc67a2dffc56dfe3411ab.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/script.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/script.8abdc67a2dffc56dfe3411ab.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/units.dd00988ca6ad6f6ecf5cfc04.raw.stderr.txt | gzip > $ast_out_dir/units.dd00988ca6ad6f6ecf5cfc04.raw.ast.json.gz; echo $? > $ast_out_dir/units.dd00988ca6ad6f6ecf5cfc04.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/units.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/units.dd00988ca6ad6f6ecf5cfc04.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/ae.f24db4e021630c8104fe333a.raw.stderr.txt | gzip > $ast_out_dir/ae.f24db4e021630c8104fe333a.raw.ast.json.gz; echo $? > $ast_out_dir/ae.f24db4e021630c8104fe333a.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/ae.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/ae.f24db4e021630c8104fe333a.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/zmalloc.7304209791027e8e4cbf718b.raw.stderr.txt | gzip > $ast_out_dir/zmalloc.7304209791027e8e4cbf718b.raw.ast.json.gz; echo $? > $ast_out_dir/zmalloc.7304209791027e8e4cbf718b.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/zmalloc.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/zmalloc.7304209791027e8e4cbf718b.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/http_parser.b6a1bc71bbcb50e0ef9e78d3.raw.stderr.txt | gzip > $ast_out_dir/http_parser.b6a1bc71bbcb50e0ef9e78d3.raw.ast.json.gz; echo $? > $ast_out_dir/http_parser.b6a1bc71bbcb50e0ef9e78d3.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c src/http_parser.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/http_parser.b6a1bc71bbcb50e0ef9e78d3.raw.ll
cd /legacy/wrk
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -ast-dump=json -fsyntax-only 2> $ast_out_dir/bytecode.d370d719881ca7bc283edac8.raw.stderr.txt | gzip > $ast_out_dir/bytecode.d370d719881ca7bc283edac8.raw.ast.json.gz; echo $? > $ast_out_dir/bytecode.d370d719881ca7bc283edac8.raw.retcode.txt
clang -I/usr/include/luajit-2.1 -c obj/bytecode.c -Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o $ast_out_dir/bytecode.d370d719881ca7bc283edac8.raw.ll
