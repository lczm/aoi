aoi:
	python3 main.py file.aoi > test.qbe && ./qbe -o asm.s test.qbe && gcc asm.s -o test && ./test

test: tests.py
	python3 tests.py

