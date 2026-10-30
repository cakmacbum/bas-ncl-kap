"""Torisferik bomba — eksenel simetrik ince kabuk (Reissner–Meissner / Love) referans çözümü.

Doğrulama aracı (V1, referans B). Üretim kodunda kullanılmaz.

Meridyen orta yüzeyde üç bölüt: taç küre (R1 = Lm) → hamut torus (R1 = rm) → silindir.
Birinci mertebe sistem, kartezyen kesit kuvvetleriyle (bölüt sınırlarında doğrudan sürekli):

    durum y = [u_r, u_z, chi, H, M_s]     (V kapalı bombe için analitik: r·V = −p·r²/2)

    ψ: meridyen teğet açısı (dr/ds = cosψ, dz/ds = sinψ, dψ/ds = −1/R1), dış normal n = (−sinψ, cosψ)
    N_s = cH + sV,  Q = −sH + cV          (c = cosψ, s = sinψ)
    ε_θ = u_r/r,  ε_s = N_s/K − ν ε_θ,  N_θ = E t ε_θ + ν N_s            (K = E t/(1−ν²))
    κ_θ = −chi·c/r, κ_s = M_s/D − ν κ_θ, M_θ = D(1−ν²) κ_θ + ν M_s       (D = E t³/12(1−ν²))
    u_r' = c ε_s − s chi,  u_z' = s ε_s + c chi,  chi' = −κ_s
    (rH)' = N_θ + p r s,   (r M_s)' = r Q + c M_θ

Denklemler sanal iş ilkesinden türetilmiştir (Kirchhoff–Love, küçük şekil değiştirme).
Yüzey gerilmeleri: σ = N/t ± 6M/t² (dış/iç); M = D·κ, κ dışbükeylik artışı. Çözüm: scipy.integrate.solve_bvp, her bölüt
[0,1]'e eşlenip istiflenir (3×5 = 15 durum), sınırlarda süreklilik koşulları.

Sınır koşulları: taçta kutuptan φ0 açısında membran kenar (u_z=0, H=pLm/2·cosψ0, M_s=0);
silindir ucunda simetri düzlemi (chi=0, H=0).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_bvp


@dataclass
class ShellResult:
    s: np.ndarray        # meridyen yay boyu (kutuptan φ0'dan itibaren), mm
    r: np.ndarray
    z: np.ndarray
    segment: np.ndarray  # 0 taç, 1 hamut, 2 silindir
    N_s: np.ndarray
    N_t: np.ndarray
    M_s: np.ndarray
    M_t: np.ndarray
    u_r: np.ndarray
    Q: np.ndarray        # enine kesme kuvveti, N/mm
    t: float
    success: bool

    def surface(self):
        """(σs_iç, σθ_iç, σs_dış, σθ_dış) MPa."""
        t = self.t
        # M = D·κ, κ = dış normal yönünde dışbükeylik artışı → dış lif ε = ε0 + (t/2)·κ
        return (self.N_s / t - 6 * self.M_s / t**2, self.N_t / t - 6 * self.M_t / t**2,
                self.N_s / t + 6 * self.M_s / t**2, self.N_t / t + 6 * self.M_t / t**2)

    def vm_surface(self) -> np.ndarray:
        si, ti, so, to = self.surface()
        vm = lambda a, b: np.sqrt(a * a - a * b + b * b)
        return np.maximum(vm(si, ti), vm(so, to))

    def max_vm(self, segment: int | None = None) -> float:
        v = self.vm_surface()
        if segment is not None:
            v = v[self.segment == segment]
        return float(v.max())


def _geometry(Di: float, t: float, L: float, rk: float, l_cyl: float, phi0: float):
    """Orta yüzey yarıçapları ve bölüt uzunlukları. Girdi: iç yüzey L, rk, Di."""
    Lm, rm, Rm = L + t / 2, rk + t / 2, Di / 2 + t / 2
    if not (Lm > rm and Rm > rm and Lm >= Rm):
        raise ValueError("geçersiz torisferik geometri")
    alpha = np.arcsin(min(1.0, (Rm - rm) / (Lm - rm)))  # taç yarı açısı (Lm=Rm → yarımküre)
    if phi0 >= alpha:
        raise ValueError("phi0 taç açısından küçük olmalı")
    return Lm, rm, Rm, alpha, [Lm * (alpha - phi0), rm * (np.pi / 2 - alpha), l_cyl]


def solve_torispherical(Di: float, t: float, L: float, rk: float, P: float = 1.0,
                        E: float = 200000.0, nu: float = 0.3, l_cyl: float | None = None,
                        phi0_deg: float = 5.0, n_nodes: int = 400, tol: float = 1e-6) -> ShellResult:
    Lm, rm, Rm, alpha, lens = _geometry(Di, t, L, rk, l_cyl if l_cyl is not None else 1.5 * Di,
                                        np.radians(phi0_deg))
    phi0 = np.radians(phi0_deg)
    K = E * t / (1 - nu**2)
    D = E * t**3 / (12 * (1 - nu**2))
    # Ölçekler (koşullanma için boyutsuz durum)
    sc = np.array([P * Rm**2 / (E * t), P * Rm**2 / (E * t), P * Rm / (E * t), P * Rm, P * Rm * t])

    # Bölüt başlangıç noktaları (kutup tarafı başlangıcı)
    zc0 = 0.0  # taç küre merkezinin z'si (keyfi)

    def geom(k: int, x: np.ndarray):
        """Bölüt k, x∈[0,1] → r, z, ψ, 1/R1."""
        sl = lens[k] * x
        if k == 0:
            phi = phi0 + sl / Lm
            return Lm * np.sin(phi), zc0 + Lm * np.cos(phi), -phi, np.full_like(x, 1 / Lm)
        zk = zc0 + Lm * np.cos(alpha) - rm * np.cos(alpha)  # torus merkezi z
        rck = Rm - rm
        if k == 1:
            phi = alpha + sl / rm
            return rck + rm * np.sin(phi), zk + rm * np.cos(phi), -phi, np.full_like(x, 1 / rm)
        return np.full_like(x, Rm), zk - sl, np.full_like(x, -np.pi / 2), np.zeros_like(x)

    def rhs_seg(k, x, Y):
        r, _, psi, _ = geom(k, x)
        c, s = np.cos(psi), np.sin(psi)
        ur, uz, chi, H, Ms = (Y * sc[:, None])
        V = -P * r / 2
        Ns = c * H + s * V
        Q = -s * H + c * V
        et = ur / r
        es = Ns / K - nu * et
        Nt = E * t * et + nu * Ns
        kt = -chi * c / r
        ks = Ms / D - nu * kt
        Mt = D * (1 - nu**2) * kt + nu * Ms
        d = np.vstack([
            c * es - s * chi,
            s * es + c * chi,
            -ks,
            (Nt + P * r * s - c * H) / r,
            (r * Q + c * Mt - c * Ms) / r,
        ])
        return d * lens[k] / sc[:, None]

    def fun(x, Y):
        return np.vstack([rhs_seg(k, x, Y[5 * k:5 * k + 5]) for k in range(3)])

    def bc(Ya, Yb):
        H0 = P * Lm / 2 * np.cos(phi0) / sc[3]
        res = [Ya[1], Ya[3] - H0, Ya[4]]
        for k in range(2):
            res += list(Yb[5 * k:5 * k + 5] - Ya[5 * (k + 1):5 * (k + 1) + 5])
        res += [Yb[12], Yb[13]]
        return np.array(res)

    # Başlangıç tahmini: membran
    x = np.linspace(0, 1, n_nodes)
    Y0 = np.zeros((15, x.size))
    for k in range(3):
        r, _, psi, _ = geom(k, x)
        c = np.cos(psi)
        if k == 2:
            Y0[5 * k] = (P * Rm / t) * (1 - nu / 2) * Rm / E / sc[0]
        else:
            Y0[5 * k] = (P * Lm / (2 * t)) * (1 - nu) * r / E / sc[0]
            Y0[5 * k + 3] = P * Lm / 2 * c / sc[3]
    sol = solve_bvp(fun, bc, x, Y0, tol=tol, max_nodes=200000)

    xs = np.linspace(0, 1, 4001)
    S, R, Z, SEG, NS, NT, MS, MT, UR, QQ = ([] for _ in range(10))
    s_off = 0.0
    Yall = sol.sol(xs)
    for k in range(3):
        Y = Yall[5 * k:5 * k + 5] * sc[:, None]
        r, z, psi, _ = geom(k, xs)
        c, s = np.cos(psi), np.sin(psi)
        V = -P * r / 2
        Ns = c * Y[3] + s * V
        et = Y[0] / r
        Nt = E * t * et + nu * Ns
        kt = -Y[2] * c / r
        Mt = D * (1 - nu**2) * kt + nu * Y[4]
        S.append(s_off + lens[k] * xs); R.append(r); Z.append(z); SEG.append(np.full(xs.size, k))
        NS.append(Ns); NT.append(Nt); MS.append(Y[4]); MT.append(Mt); UR.append(Y[0]); QQ.append(-s * Y[3] + c * V)
        s_off += lens[k]
    cat = np.concatenate
    return ShellResult(cat(S), cat(R), cat(Z), cat(SEG), cat(NS), cat(NT), cat(MS), cat(MT), cat(UR), cat(QQ), t,
                       bool(sol.success))


if __name__ == "__main__":  # pragma: no cover
    for rk_d in (0.06, 0.10, 0.17):
        res = solve_torispherical(1000, 10, 1000, rk_d * 1000)
        print(f"rk/D={rk_d}: max vm {res.max_vm():.1f}  hamut {res.max_vm(1):.1f}  ok={res.success}")
