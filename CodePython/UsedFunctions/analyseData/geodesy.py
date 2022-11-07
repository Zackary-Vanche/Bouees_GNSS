import numpy as np

# global variables : parameters for ellipsoid GRS80
a = 6378137
e2 = 0.006694380022

b = np.sqrt(a ** 2 * (1 - e2))
ep2 = (a ** 2 - b ** 2) / (b ** 2)
f = (a - b) / a
k0 = 0.9996
omega_eura = np.array([-0.085, -0.531, 0.770])  # en mas/an (1 miliarcseconde = 1e-3" = 1e-3/3600 °)


# ATTENTION : les angles doivent être exprimés en radians

def convert_rad(lon, lat):
    return lon * np.pi / 180, lat * np.pi / 180


def convert_deg(lon, lat):
    return lon * 180 / np.pi, lat * 180 / np.pi


def geod2ecef(lon, lat, hgt):
    lon, lat = convert_rad(lon, lat)

    v = np.sqrt(1 - e2 * (np.sin(lat)) ** 2)
    N = a / v

    x = (N + hgt) * np.cos(lon) * np.cos(lat)
    y = (N + hgt) * np.sin(lon) * np.cos(lat)
    z = (N * (1 - e2) + hgt) * np.sin(lat)

    return x, y, z


def ecef2geod(x, y, z):
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    mu = np.arctan(z / (np.sqrt(x ** 2 + y ** 2)) * ((1 - f) + a * e2 / r))

    lon = np.arctan(y / x)
    lat = np.arctan(
        (z * (1 - f) + e2 * a * (np.sin(mu)) ** 3) / ((1 - f) * (np.sqrt(x ** 2 + y ** 2) - e2 * a * np.cos(mu) ** 3)))
    hgt = np.sqrt(x ** 2 + y ** 2) * np.cos(lat) + z * np.sin(lat) - a * np.sqrt(1 - e2 * np.sin(lat) ** 2)

    lon, lat = convert_deg(lon, lat)

    return lon, lat, hgt


def enu2geod(lon0, lat0, hgt0, e, n, u):
    x0, y0, z0 = geod2ecef(lon0, lat0, hgt0)
    lon0, lat0 = convert_rad(lon0, lat0)

    R = np.array([[-np.sin(lon0), np.cos(lon0), 0],
                  [-np.sin(lat0) * np.cos(lon0), -np.sin(lat0) * np.sin(lon0), np.cos(lat0)],
                  [np.cos(lat0) * np.cos(lon0), np.cos(lat0) * np.sin(lon0), np.sin(lat0)]])

    X0 = np.array([x0, y0, z0])
    ENU = np.array([e, n, u])
    X = X0 + np.linalg.inv(R) @ ENU
    x, y, z = X
    lon, lat, hgt = ecef2geod(x, y, z)

    return lon, lat, hgt


def geod2enu(lon0, lat0, hgt0, lon, lat, hgt):
    """
    Conversion des coordonnées géographiques lat, lon, hauteur en coordonnées locales E, N, U
    :param lon0: Longitude du centre du repère local
    :param lat0: Latitude du centre du repère local
    :param hgt0: Hauteur du centre du repère local
    :param lon: Longitude du point considéré
    :param lat: Latitude du point considéré
    :param hgt: Hauteur du point considéré
    :return:
    """
    x0, y0, z0 = geod2ecef(lon0, lat0, hgt0)
    x, y, z = geod2ecef(lon, lat, hgt)

    lon0, lat0 = convert_rad(lon0, lat0)
    lon, lat = convert_rad(lon, lat)

    R = np.array([[-np.sin(lon0), np.cos(lon0), 0],
                  [-np.sin(lat0) * np.cos(lon0), -np.sin(lat0) * np.sin(lon0), np.cos(lat0)],
                  [np.cos(lat0) * np.cos(lon0), np.cos(lat0) * np.sin(lon0), np.sin(lat0)]])

    X = np.array([x - x0, y - y0, z - z0]).T
    A = R @ X
    e, n, u = A

    return e, n, u


def utm_mu(n, lon, lat):
    lon, lat = convert_rad(lon, lat)
    lon0 = (6 * (n - 31) + 3) * (np.pi / 180)
    vp2 = 1 + ep2 * (np.cos(lat) ** 2)
    mu = k0 * (1 + 1 / 2 * vp2 * (lon - lon0) ** 2 * np.cos(lat) ** 2)
    return mu


def utm_gamma(n, lon, lat):
    lon, lat = convert_rad(lon, lat)
    lon0 = (6 * (n - 31) + 3) * (np.pi / 180)
    gamma = (lon - lon0) * np.sin(lat) * (1 + 1 / 3 * (lon - lon0) ** 2 * np.cos(lat) ** 2)
    return gamma


def beta(lat):
    """
    Longeur d'un arc méridien entre un point quelconque de latitude lat et l'équateur
    On calcul ici une valeur approchée de beta ne comprenant que les 5 premiers termes
    L'erreur est inférieure à 1mm
    :param lat:
    :return:
    """
    lat = lat * np.pi / 180
    e = np.sqrt(e2)
    b_0 = 1 - 0.25 * e ** 2 - (3 / 64) * e ** 4 - (5 / 256) * e ** 6 - (175 / 16384) * e ** 8
    b_1 = -(105 / 4096) * e ** 8 - (45 / 1024) * e ** 6 - (3 / 32) * e ** 4 - (3 / 8) * e ** 2
    b_2 = (525 / 16384) * e ** 8 + (45 / 1024) * e ** 6 + (15 / 256) * e ** 4
    b_3 = -(175 / 12288) * e ** 8 - (35 / 3072) * e ** 6
    b_4 = (315 / 131072) * e ** 8
    beta = a * (b_0 * lat + b_1 * np.sin(2 * lat) + b_2 * np.sin(4 * lat) + b_3 * np.sin(6 * lat) + b_4 * np.sin(
        8 * lat))
    return beta


def utm_geod2map(n, lon, lat):
    """
    Calcul les coordonnées X, Y en UTM correspondant aux coordonnées géographiques (lon, lat) pour la zone UTM numéro n
    :param n: numéro de la zone UTM
    :param lon: longitude géographique
    :param lat: latitude géographique
    :return: coordonnées UTM
    """
    b = beta(lat)
    lon, lat = convert_rad(lon, lat)
    X0 = 500000

    if lat > 0:  # On est dans l'hémisphère Nord
        Y0 = 0
    else:  # On est dans l'hémisphère Sud
        Y0 = 10000000

    n1 = np.sqrt(1 + ep2 * np.cos(lat) ** 4)
    v = np.sqrt(1 - e2 * np.sin(lat))
    vp = np.sqrt(1 + ep2 * np.cos(lat) ** 2)
    rho = a * (1 - e2) / v ** 3
    N = a / v
    lon0 = (6 * (n - 31) + 3) * (np.pi / 180)

    x_utm = X0 + k0 * (np.sqrt(rho * N) / 2) * np.log(
        (n1 + vp * np.cos(lat) * np.sin(n1 * (lon - lon0))) / (n1 - vp * np.cos(lat) * np.sin(n1 * (lon - lon0))))

    y_utm = Y0 + k0 * b + k0 * np.sqrt(rho * N) * (
            np.arctan(np.tan(lat) / (vp * np.cos(n1 * (lon - lon0)))) - np.arctan(np.tan(lat) / vp))

    return x_utm, y_utm

def utm_geod2mapOpti(n, lon, lat):
    """
    Calcul les coordonnées X, Y en UTM correspondant au coordonnées géographiques (lon, lat) pour la zone UTM numéro n
    Version optimisée pour la gestion de gros dataset
    :param n: numéro de la zone UTM
    :param lon: longitude géographique
    :param lat: latitude géographique
    :return: coordonnées UTM
    """
    b = beta(lat)
    lon, lat = convert_rad(lon, lat)
    X0 = 500000

    # if lat > 0:  # On est dans l'hémisphère Nord
    #     Y0 = 0
    # else:  # On est dans l'hémisphère Sud
    #     Y0 = 10000000

    Y0 = np.zeros(lat.shape)
    idx_1 = np.where(lat > 0)
    Y0[idx_1] = 0
    idx_2 = np.where(lat <= 0)
    Y0[idx_2] = 10000000

    n1 = np.sqrt(1 + ep2 * np.cos(lat) ** 4)
    v = np.sqrt(1 - e2 * np.sin(lat))
    vp = np.sqrt(1 + ep2 * np.cos(lat) ** 2)
    rho = a * (1 - e2) / v ** 3
    N = a / v
    lon0 = (6 * (n - 31) + 3) * (np.pi / 180)

    x_utm = X0 + k0 * (np.sqrt(rho * N) / 2) * np.log(
        (n1 + vp * np.cos(lat) * np.sin(n1 * (lon - lon0))) / (n1 - vp * np.cos(lat) * np.sin(n1 * (lon - lon0))))

    y_utm = Y0 + k0 * b + k0 * np.sqrt(rho * N) * (
            np.arctan(np.tan(lat) / (vp * np.cos(n1 * (lon - lon0)))) - np.arctan(np.tan(lat) / vp))

    return x_utm, y_utm


def utm_map2geod(n, X, Y):
    lon, lat = np.nan, np.nan
    # ...
    return lon, lat


def geod2iso(lat):
    """
    Conversion de la latitude géographique en latitude isométrique
    :param lat:
    :return:
    """
    lat_iso = np.log(
        np.tan(np.pi / 4 + lat / 2) * ((1 - np.sqrt(e2) * np.sin(lat)) / (1 + np.sqrt(e2) * np.sin(lat))) ** (
                (np.sqrt(e2)) / 2))
    return lat_iso


def get_vel(X):
    """
    Calcul du vecteur vitesse associé au point de coordonnées X
    :param X:
    :return:
    """
    omega = omega_eura * (1e-3 / 3600) * (np.pi / 180)  # omega_eura en radians / an
    Xdot = np.cross(omega, X)
    return Xdot


def apply_vel(P0, Pdot, t0, ti):
    """
    Translation des paramètres de similitudes à la date ti
    :param P0: paramètres de similitude (vecteur numpy) à la date t0
    :param Pdot: dérivée temporelle des paramètres de similitude (vecteur numpy) à la date t0
    :param t0: date à laquelle sont exprimés les paramètres de similitudes
    :param ti: date à laquelle on souhaite translater les paramètres de similitudes
    :return: paramètres de similitude à la date ti
    """
    Pi = P0 + (ti - t0) * Pdot
    return Pi


def get_similitude(t_cible):
    """
    Calcul des paramètres de similitudes permettant le passage de l'ITRF2014 à l'ETRF2000 à l'époque t_cible
    :param t_cible:
    :return:
    """
    coef_mas_to_rad = (1e-3 / 3600) * (np.pi / 180)
    t0 = 2000.0
    # Paramètres de similitudes pour le passage de l'ITRF2014 à l'ETRF2000(Ryy) à t0 = 2000.0
    Tx, Ty, Tz = 53.7 * 1e-3, 51.2 * 1e-3, -55.1 * 1e-3
    Tx_dot, Ty_dot, Tz_dot = 0.1 * 1e-3, 0.1 * 1e-3, -1.9 * 1e-3
    d = 1.02 * 1e-9
    d_dot = 0.11 * 1e-9
    eps_x, eps_y, eps_z = 0.891 * coef_mas_to_rad, 5.390 * coef_mas_to_rad, -8.712 * coef_mas_to_rad
    eps_x_dot, eps_y_dot, eps_z_dot = 0.081 * coef_mas_to_rad, 0.49 * coef_mas_to_rad, -0.792 * coef_mas_to_rad

    P0 = np.array([Tx, Ty, Tz, d, eps_x, eps_y, eps_z])
    Pdot = np.array([Tx_dot, Ty_dot, Tz_dot, d_dot, eps_x_dot, eps_y_dot, eps_z_dot])

    P = apply_vel(P0, Pdot, t0, t_cible)  # Paramètre de la similitude translaté à t_cible
    T_i = P[0:3]
    eps_i = P[4:7]
    d_i = P[3]
    R_i = np.array([[1, -eps_i[2], eps_i[1]],
                    [eps_i[2], 1, -eps_i[0]],
                    [-eps_i[1], eps_i[0], 1]])

    return T_i, R_i, d_i


def itrf2rgf(Xitrf, t_i):
    """
    Passage de L'ITRF2014 au RGF93
    :param Xitrf: coordonnées du point à la date t_i dans l'ITRF2014
    :param t_i:
    :return:
    """
    t_rgf93 = 2009.0
    X_itrf_2009 = apply_vel(Xitrf, get_vel(Xitrf), t_i, t_rgf93)  # Coordonnées dans l'ITF2014 à l'époque 2009.0

    T_i, R_i, d_i = get_similitude(t_rgf93)  # Paramètres de similitude pour le passage de ITR2014 à ETRF2000 à l'époque 2009.0
                                             # Ces paramètres permettent donc le passage dans le repère RGF93 = ETRF2000 (2009.0)
    X_r = T_i + (d_i * np.eye(3) + R_i) @ X_itrf_2009   # Convertion des coordonnées dans le RGF93

    return X_r


def L93_geod2map(lon, lat, hgt):
    """
    Projection en Lambert93 des coordonées géographiques exprimées dans le repère RGF93
    :param lon:
    :param lat:
    :param hgt:
    :return:
    """
    lon, lat = convert_rad(lon, lat)
    lon0 = 3 * np.pi / 180
    X0, Y0 = 700 * 1e3, 6600 * 1e3

    phi_1, phi_2 = 44, 49
    phi_0 = 1 / 2 * (phi_1 + phi_2)
    phi_0, phi_1, phi_2 = phi_0 * np.pi / 180, phi_1 * np.pi / 180, phi_2 * np.pi / 180

    v1, v2 = np.sqrt(1 - e2 * (np.sin(phi_1)) ** 2), np.sqrt(1 - e2 * (np.sin(phi_2)) ** 2)
    N1, N2 = a / v1, a / v2
    L0, L1, L2 = geod2iso(phi_0), geod2iso(phi_1), geod2iso(phi_2)

    L = geod2iso(lat)
    n = 1 / (L1 - L2) * np.log((N2 * np.cos(phi_2)) / (N1 * np.cos(phi_1)))
    C = (N1 * np.cos(phi_1) / n) * np.exp(n * L1)
    R0 = C * np.exp(-n * L0)

    Xp = X0
    Yp = Y0 + R0

    X = Xp + C * np.exp(-n * L) * np.sin(n * (lon - lon0))
    Y = Yp - C * np.exp(-n * L) * np.cos(n * (lon - lon0))

    return X, Y, hgt


if __name__ == "__main__":
    print("Geodesy Tollbox")
    x, y, z = 4231162.788, -332746.920, 4745130.689
    lon, lat, hgt = -4.49659762, 48.38049068, 65.806

    x1, y1, z1 = geod2ecef(lon, lat, hgt)
    print("Convertion geographique vers ecef  \n "
          "(lambda, phi, h) = ({0}, {1}, {2}) \n -->  (x, y, z) = ({3}, {4}, {5})".format(lon, lat, hgt, x1, y1, z1))

    lon1, lat1, hgt1 = ecef2geod(x, y, z)
    print("Convertion ecef vers geographique \n "
          " (x, y, z)= ({0}, {1}, {2}) \n -->  (lambda, phi, h) = ({3}, {4}, {5})".format(x, y, z, lon1, lat1, hgt1))

    lon, lat, hgt = -4.49659762, 48.38049068, 65.806
    lon0, lat0, hgt0 = -4.49700000, 48.38000000, 65.000
    e, n, u = 29.807, 54.563, 0.806

    e1, n1, u1 = geod2enu(lon0, lat0, hgt0, lon, lat, hgt)
    print("Convertion geographique vers ENU \n "
          " (lon, lat, hgt)= ({0}, {1}, {2}) \n -->  (e, n, u) = ({3}, {4}, {5})".format(lon, lat, hgt, e1, n1, u1))

    lon1, lat1, hgt1 = enu2geod(lon0, lat0, hgt0, e, n, u)
    print("Convertion ENU vers geographique \n "
          " (e, n ,u)= ({0}, {1}, {2}) \n -->  (lon , lat, hgt) = ({3}, {4}, {5})".format(e, n, u, lon1, lat1, hgt1))

    lon, lat, n = -4.49659762, 48.38049068, 30
    mu = utm_mu(n, lon, lat)
    gamma = utm_gamma(n, lon, lat)
    b = beta(lat)
    print("Calcul de mu et gamma \n "
          "mu = {0} \n"
          "gamma = {1} \n"
          "beta = {2}".format(mu, gamma, beta))

    X, Y = utm_geod2map(n, lon, lat)
    print("Projection en UTM{0} \n "
          "(n, lon, lat) = ({0}, {1}, {2}) --> X = {3}m, Y = {4}m ".format(n, lon, lat, X, Y))

    print("omega eura en radians : ", omega_eura * (1e-3 / 3600) * (np.pi / 180))
