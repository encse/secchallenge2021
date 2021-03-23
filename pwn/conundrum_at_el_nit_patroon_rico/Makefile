all: main.cpp mefw_generated.h
	g++ -Iflatbuffers/include  main.cpp -o generate_input

run: all
	./generate_input

send:
	echo `stat -c%s input` > x.x
	cat input >> x.x
	nc challenges.crysys.hu 5010 < x.x
