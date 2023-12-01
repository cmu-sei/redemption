#TODO: Rewrite this to use PyTest

# <legal></legal>

~/acr-demo/MemSafetyFR3/prototool/c-to-json.sh test01.c test01
diff -s test01.n.json test01.parser.answer.json

python3 ~/make-monitoring/ast2source/ast2source.py --ast-path test01.repaired.json --source-dir . --dest-dir out
diff -s out/test01.c test01.repaired.answer.c
