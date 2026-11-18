# Independent check with python-flint (not qSage): self-similar form at level alpha.
import sys, time, flint
E=40; M=2**E
def eta(step,T):
    c=[0]*T; c[0]=1; k=1
    while True:
        a=step*(k*(3*k-1)//2); b=step*(k*(3*k+1)//2)
        if a>=T: break
        s=-1 if k%2 else 1
        c[a]=s%M
        if b<T: c[b]=s%M
        k+=1
    return flint.nmod_poly(c,M)
def v2(x):
    x=int(x)%M
    return E if x==0 else (x & -x).bit_length()-1
p=int(sys.argv[1]); al=int(sys.argv[2]); T=int(sys.argv[3])
t=time.time()
B=(eta(4,T)*eta(1,T).inverse_series_trunc(T)).truncate(T)
print("built",T,"coeffs in %.1fs"%(time.time()-t),[int(B[i]) for i in range(8)])
A=p**(2**al-1); d=(p**(2**al)-1)//8
N=(T-1-d)//A+1
a=[int(B[A*n+d]) for n in range(N)]
c=a[0]
kz=min([v2(a[n]) for n in range(N) if n%p] or [E])
km=min([v2(a[p*m]-c*int(B[m])) for m in range(1,(N-1)//p+1)] or [E])
print(f"p={p} alpha={al}: progression {A}n+{d}, {N} terms; min v2 on p∤n = {kz}; min v2 of a(pm)-c*b4(m) = {km} ({(N-1)//p} multiples); c mod 2^10 = {c%1024}")
