gfortran -fPIC -O3 -c quadpack_double.f90
f2py -m VSMFortran --fcompiler=gfortran --f90flags='-fopenmp' -lgomp \
  -I. quadpack_double.o\
  -c math.f90 models.f90
mv VSMFortran.cpython-* ../.