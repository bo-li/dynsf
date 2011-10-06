__all__ = ['fourier_cos', 'general_sin_integral', 'general_cos_integral']

from numpy import sin, cos, pi, mod, \
    zeros, arange, linspace, require, \
    where, sum


__doc__ = """
For information about Filon's formula, see e.g.
Abramowitz Stegun, section 25,
http://mathworld.wolfram.com/FilonsIntegrationFormula.html,
Allen Tildesley, Appendix D.

If the argument f is a 2D-array, the transformation is done along each individual
column (axis=0). I.e.

 [F0[0]  F1[0] ..  FN[0] ]     [f0[0]  f1[0] ..  fN[0] ]
 [   .      .         .  ]     [   .      .         .  ]
 [F0[.]  F1[.] ..  FN[.] ] = I([f0[.]  f1[.] ..  fN[.] ], dx, [k[0] .. k[Nk]])
 [   .      .         .  ]     [   .      .         .  ]
 [F0[Nk] F1[Nk] .. FN[Nk]]     [f0[Nx] f1[Nx] .. fN[Nx]]

where k and Fj have end index Nk, and fj have end index Nx.
Nk is arbitrarily, and is derived from the length of k.
Nx must be an even number (i.e. fj should have an odd length).

general_sin_integral and general_cos_integral allows for shifted 
x-intervals by the optional argument x0.

"""


def fourier_cos(f, dx, k=None):
    """Calculate a direct fourier cosine transform of function f(x) using 
    Filon's integration method

    k, F = fourier_cos(f, dx)
    Array values f[0]..f[2n] is expected to correspond to f(0.0)..f(2n*dx),
    hence, it should contain an odd number of elements.
    The transform is approximated with the integral (xmax = 2n*dx)
    2*\int_{0}^{xmax} 

    """ 
    
    if k is None:
        k = linspace(0.0, pi/dx, f.shape[0])

    return k, 2*general_cos_integral(f, dx, k, x0=0.0)


def general_cos_integral(f, dx, k, x0=0.0):
    """\int_{x0}^{2n*dx} f(x)*cos(k x) dx
    
    f must have length 2n+1.
    """ 
    return _gen_sc_int(f, dx, k, x0, cos)

def general_sin_integral(f, dx, k, x0=0.0):
    """\int_{x0}^{2n*dx} f(x)*sin(k x) dx
    
    f must have length 2n+1.
    """ 
    return _gen_sc_int(f, dx, k, x0, sin)


def _gen_sc_int(f, dx, k, x0, sc):

    f = require(f)
    k = require(k)

    f_original_shape = f.shape
    
    if len(f.shape) == 1:
        f = f.reshape(f.shape+(1,1))
    elif len(f.shape) == 2:
        f = f.reshape(f.shape+(1,))
    else:
        raise RuntimeError('that many dimensions on f are currently not supported')

    if len(k.shape) != 1:
        raise RuntimeError('k should be one dimensional')
    Nk = len(k)

    N = f_original_shape[0]
    Nmax = N-1
    if mod(Nmax, 2) != 0 or N < 3:
        raise RuntimeError('f should have an odd length (>2) along its first axis')

    # Split into even (E) and odd (O) indexed parts
    fE = f[0::2,:,:]
    fO = f[1::2,:,:]

    # axis=3 spans the reciprocal (k) dimension
    k = k.reshape((1,1,Nk))
    x = (x0+dx*arange(0.0, N)).reshape((N,1,1))

    alpha, beta, gamma = _alpha_beta_gamma(dx*k)

    sc_k_x = sc(k*x)

    sc_k_x[0,:,:] *= 0.5
    sc_k_x[Nmax,:,:] *= 0.5
    sc_k_xE = sc_k_x[0::2,:,:]
    sc_k_xO = sc_k_x[1::2,:,:]
            
    if sc == sin:
        F = dx*(alpha*(f[0,:,:]*cos(k*x0) - f[Nmax,:,:]*cos(k*x[Nmax,0,0])) +
                beta*sum(fE*sc_k_xE, axis=0) + gamma*sum(fO*sc_k_xO, axis=0))
    elif sc == cos:
        F = dx*(alpha*(f[Nmax,:,:]*sin(k*x[Nmax,:,:]) - f[0,:,:]*sin(k*x0)) +
                beta*sum(fE*sc_k_xE, axis=0) + gamma*sum(fO*sc_k_xO, axis=0))
    else:
        raise RuntimeError('Internal error')
    
    F = F.transpose(2,1,0).reshape((Nk,) + f_original_shape[1:])
    return F


def _alpha_beta_gamma(theta):
    # From theta, calculate alpha, beta, and gamma
    # theta is expected to have shape (1,1,N)

    N = theta.size
    alpha = zeros((1,1,N))
    beta = zeros((1,1,N))
    gamma = zeros((1,1,N))

    # theta==0 needs special treatment
    I_nz = theta.nonzero()[2]
    I_z = where(theta==0.0)[2]
    if I_z.size > 0:
        beta[:,:,I_z] = 2.0/3.0
        gamma[:,:,I_z] = 4.0/3.0
        theta = theta[:,:,I_nz]

    sin_t = sin(theta)
    cos_t = cos(theta)
    sin2_t = sin_t*sin_t
    cos2_t = cos_t*cos_t
    theta2 = theta*theta
    itheta3 = 1.0/(theta2*theta)
    
    alpha[:,:,I_nz] = itheta3*(theta2 + theta*sin_t*cos_t - 2*sin2_t)
    beta[:,:,I_nz] = 2*itheta3*(theta*(1+cos2_t) - 2*sin_t*cos_t)
    gamma[:,:,I_nz] = 4*itheta3*(sin_t - theta*cos_t)

    return alpha, beta, gamma



