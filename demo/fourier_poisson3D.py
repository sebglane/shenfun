r"""
Solve Poisson equation on (0, 2pi)x(0, 2pi) with periodic bcs

    \nabla^2 u = f, u(2pi, y) = u(0, y), u(x, 2pi) = u(x, 0)

Use Fourier basis

"""
from sympy import Symbol, cos, sin, exp, lambdify
import numpy as np
import matplotlib.pyplot as plt
from shenfun.fourier.bases import R2CBasis, C2CBasis
from shenfun.tensorproductspace import TensorProductSpace
import shenfun
from shenfun import inner_product
from mpi4py import MPI

comm = MPI.COMM_WORLD

# Use sympy to compute a rhs, given an analytical solution
x = Symbol("x")
y = Symbol("y")
z = Symbol("z")
u = cos(4*x) + sin(8*y) + sin(6*z)
#u = exp(1j*4*x)
f = u.diff(x, 2) + u.diff(y, 2) + u.diff(z, 2)

ul = lambdify((x, y, z), u, 'numpy')
fl = lambdify((x, y, z), f, 'numpy')

# Size of discretization
N = 32

K0 = C2CBasis(N)
K1 = C2CBasis(N)
K2 = R2CBasis(N)
T = TensorProductSpace(comm, (K0, K1, K2))
X = T.local_mesh(True) # With broadcasting=True the shape of X is local_shape, even though the number of datapoints are still the same as in 1D

# Get f on quad points
fj = fl(X[0], X[1], X[2])

# Compute right hand side
f_hat = T.scalar_product(fj)

# Solve Poisson equation
Laplace = shenfun.tensorproductspace.Laplace
v = T.test_function()
A = shenfun.tensorproductspace.inner_product(v, Laplace(v))
f_hat = f_hat / A['diagonal']

uq = T.backward(f_hat, fast_transform=True)

uj = ul(X[0], X[1], X[2])
print(abs(uj-uq).max())
assert np.allclose(uj, uq)

plt.figure()
plt.contourf(X[0][:,:,0], X[1][:,:,0], uq[:, :, 8])
plt.colorbar()

plt.figure()
plt.contourf(X[0][:,:,0], X[1][:,:,0], uj[:, :, 8])
plt.colorbar()

plt.figure()
plt.contourf(X[0][:,:,0], X[1][:,:,0], uq[:, :, 8]-uj[:, :, 8])
plt.colorbar()
plt.title('Error')
#plt.show()

#plt.figure()
#plt.plot(points, uj)
#plt.title("U")
#plt.figure()
#plt.plot(points, uq - uj)
#plt.title("Error")
#plt.show()