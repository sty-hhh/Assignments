# README

- 串行实现

~~~python
python knn_serial.py
~~~

- mpi4py

需要安装Cython和mpi4py

~~~powershell
pip install Cython
pip install mpi4py
~~~

运行程序（4代表进程数）

~~~python
mpiexec -n 4 python knn_mpi4py.py
~~~

- pymp

需要安装pymp

~~~powershell
pip install pymp-pypi
~~~

运行程序

~~~python
python knn_pymp.py
~~~

- PyCUDA

需要安装nvcc和PyCUDA对应版本

运行程序

~~~python
python knn_pycuda.py
~~~

- sklearn

~~~python
python knn_sklearn.py
~~~

