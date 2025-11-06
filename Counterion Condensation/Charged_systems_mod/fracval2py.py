#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def Plot_2d(spheres,n):
    x = spheres["x"].values
    y = spheres["y"].values
    z = spheres["z"].values
    r = spheres["r"].values
    fig, ax = plt.subplots(figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')
    for i in range(len(x)):
        plot_one_sphere(x[i],y[i],z[i],r[i],n,ax)
    ax.set_xlabel('X position', fontsize=20)
    ax.set_ylabel('Y position', fontsize=20)
    ax.set_zlabel('Z position', fontsize=20)
    ax.view_init(azim=0, elev=90)
    plt.show()
    return

#********************************************************************************
# Read the file containing the info of the aggregate
#********************************************************************************
def Read_spheres(path, scale, normalized):
    columns= ["x", "y", "z", "r"]
    spheres = pd.read_csv(path, sep="\s+", names=columns, dtype='float')
    spheres = spheres*scale
    if normalized:
        rp_mean = np.mean(spheres["r"])
        spheres = spheres/rp_mean
        x_cm = np.mean(spheres["x"])
        y_cm = np.mean(spheres["y"])
        z_cm = np.mean(spheres["z"])
        spheres["x"] = spheres["x"]-x_cm
        spheres["y"] = spheres["y"]-y_cm
        spheres["z"] = spheres["z"]-z_cm
    # Calculate the volume of spheres
    spheres["v"] = np.power(spheres["r"],3)*np.pi*4/3
    return spheres

#********************************************************************************
# Maximum radius of an aggregate
#********************************************************************************
def Rmax_spheres(spheres):
    x_cm = np.mean(spheres["x"])
    y_cm = np.mean(spheres["y"])
    z_cm = np.mean(spheres["z"])
    R_max = 0
    for i in range(len(spheres["x"])):
        dist = np.sqrt(np.power(spheres["x"].iloc[i]-x_cm,2)+\
               np.power(spheres["y"].iloc[i]-y_cm,2)+\
               np.power(spheres["z"].iloc[i]-z_cm,2))+\
                spheres["r"].iloc[i]
        if (dist > R_max):
            R_max = dist
    return R_max

#********************************************************************************
# Calculate Mean Coordination Number (MCN)
#********************************************************************************
def MCN(Agg,spheres):
    sph = spheres.loc[Agg.name]
    Npp = len(sph)
    if (Npp==1):
        return 0
    k = 0  
    n_c_i = np.zeros(Npp)
    for i in range(0,Npp):
        xi = sph["x"].iloc[i]
        yi = sph["y"].iloc[i]
        zi = sph["z"].iloc[i]
        ri = sph["r"].iloc[i]
        
        n_c_i[i] = 0  # coordination number
        
        for j in range(i+1,Npp):
            xj = sph["x"].iloc[j]
            yj = sph["y"].iloc[j]
            zj = sph["z"].iloc[j]
            rj = sph["r"].iloc[j]
            vj = np.power(rj,3)
            sj = np.power(rj,2)
            
            dij = np.sqrt((xi-xj)**2+(yi-yj)**2+(zi-zj)**2)
            rij = ri+rj
            
            if (dij <= rij*1.000000000001 and i!=j): 
                n_c_i[i] = n_c_i[i]+2
    return np.mean(n_c_i)

#********************************************************************************
# Determine the number of primary particles in an aggregate
#********************************************************************************
def N_primary_particles(Agg,spheres):
    sph = spheres.loc[Agg.name]
    Npp = len(sph)
    return Npp

#********************************************************************************
# Read the file containing the time&position FTP
#********************************************************************************
def Read_info_ftp(path):
    columns= ["time", "r"]
    spheres = pd.read_csv(path, sep="\s+", names=columns, dtype='float')
    return spheres

#********************************************************************************
# Repulsive interaction potential forces
#********************************************************************************
def Repulsive_interaction(d, r, A,s_LJ):
    f_rep1 = A*pow(s_LJ,6)/(2520*r);
    f_rep2 = pow(d,2)*(-7/2/pow(r-d,8)-7/2/pow(r+d,8)-7/pow(r,8));
    f_rep3 = (1/15)*(-5/pow(r-d,6)-5/pow(r+d,6)+10/pow(r,6));
    f_rep4 = (-d/3)*(6/pow(r+d,7)-6/pow(r-d,7));

    f_rep5 = A*pow(s_LJ,6)/(2520*pow(r,2));
    f_rep6 = pow(d,2)*(1/2/pow(r-d,7)+1/2/pow(r+d,7)+1/pow(r,7));
    f_rep7 = (1/15)*(1/pow(r-d,5)+1/pow(r+d,5)-2/pow(r,5));
    f_rep8 = (-d/3)*(-1/pow(r+d,6)+1/pow(r-d,6));

    f_rep = -f_rep1*(f_rep2+f_rep3+f_rep4)-f_rep5*(f_rep6+f_rep7+f_rep8);
    return f_rep

#********************************************************************************
# Attractive interaction potential forces
#********************************************************************************
def Attractive_interaction(d_sum,dist, A):
    f_atr = - A*pow(d_sum,6)/(6*pow(dist,3)*pow(pow(dist,2)-pow(d_sum,2),2));
    return f_atr

#********************************************************************************
# Total interaction potential
#********************************************************************************
def Interaction_potentials(p):
    npp = len(p)-1
    f_0 = 0; f_1 = 0; f_2 = 0;

    #// distance to each monomer in the aggregate
    j_range = range(0,npp)
    for j in j_range:
        unit[0] = p[npp].x - p[j].x;
        unit[1] = p[npp].y - p[j].y;
        unit[2] = p[npp].z - p[j].z;

        dist = np.sqrt(pow(unit[0],2) + pow(unit[1],2) + pow(unit[2],2));

        unit[0] = unit[0]/dist;
        unit[1] = unit[1]/dist;
        unit[2] = unit[2]/dist;

        d_sum = 2*(p[j].r+p[j].r);
        r_cut = r_cut_factor*d_sum;

        #// Interaction potential - attractive part
        if (dist <= r_cut):
            f_atr = Attractive_interaction(d_sum, dist);
        
        #// Interaction potential - repulsive part
        f_rep = Repulsive_interaction(d_sum, dist);

        #// Interaction potential - net resulting force
        f_mag = f_atr + f_rep;
        f_0 = f_0 + f_mag*unit[0];
        f_1 = f_1 + f_mag*unit[1];
        f_2 = f_2 + f_mag*unit[2];
    F0[0] = f_0;
    F0[1] = f_1;
    F0[2] = f_2;
    return F0

#********************************************************************************
# Plot an aggregqte
#********************************************************************************
def plot_one_sphere(x,y,z,r,n,ax):
    u = np.linspace(0,2*np.pi,num=n)
    v = np.linspace(0,np.pi,num=n)

    X = x + r* np.outer(np.cos(u), np.sin(v))
    Y = y + r* np.outer(np.sin(u), np.sin(v))
    Z = z + r* np.outer(np.ones(np.size(u)), np.cos(v))

    # The rstride and cstride arguments default to 10
    ax.plot_surface(X,Y,Z, rstride=4, cstride=4)
    
def Plot_3d(spheres,n):
    x = spheres["x"].values
    y = spheres["y"].values
    z = spheres["z"].values
    r = spheres["r"].values
    fig, ax = plt.subplots(figsize=(10,10))
    ax = fig.add_subplot(111, projection='3d')
    for i in range(len(x)):
        plot_one_sphere(x[i],y[i],z[i],r[i],n,ax)
    ax.set_xlabel('X position', fontsize=20)
    ax.set_ylabel('Y position', fontsize=20)
    ax.set_zlabel('Z position', fontsize=20)
    plt.show()    

#********************************************************************************
# Save info to a .txt file
#********************************************************************************
def Export_data(file_name,x,x_size,y,y_size,f1,f2,f3):
    """
    creates a file with the output of this code
    """
    # convert to nm
    x = x*1e+09
    y = y*1e+09
    with open(file_name, 'w') as file:
        file.write("TITLE = "+file_name+"\n")
        file.write('VARIABLES ="x (nm)","y (nm)","f_atr", "f_rep", "f_tot"\n')
        file.write('ZONE T="dla2py", I = \t{} , J = \t{} , F =POINT\n'.format(x_size,y_size))
        for i in range(len(x)):
            file.write("{:.6e}\t".format(x[i]))
            file.write("{:.6e}\t".format(y[i]))
            file.write("{:.6e}\t".format(f1[i]))
            file.write("{:.6e}\t".format(f2[i]))
            file.write("{:.6e}".format(f3[i]))
            file.write("\n")
    return

#********************************************************************************
# Discretize the aggregate
#********************************************************************************
def Discretize_agg(spheres, resolution=128, fact=1):
    data, grid = discretize_spherelist(spheres, resolution, fact)
    #x, y, z = grid
    #nx, ny, nz = data.shape
    #
    #coords = np.where(data > 0)
    return data, grid

def discretize_spherelist(spheres, resolution=128, fact=1):
    """
        Discretize the aggregate in a grid
    """
    xbounds, ybounds, zbounds = surrounding_box(spheres, fact)

    (x, y, z) = mkgrid(xbounds, ybounds, zbounds, resolution)

    # fill the domain : positive value if inside at least a sphere
    data = - np.ones_like(x)*np.inf
    for i in range(len(spheres)):
        d = (spheres["x"].iloc[i] - x) ** 2 + (spheres["y"].iloc[i] - y) ** 2 + (spheres["z"].iloc[i] - z) ** 2
        data = np.maximum(data, spheres["r"].iloc[i] ** 2 - d)

    return data, (x, y, z)

def surrounding_box(spheres, fact=4):
    """
        compute dimensions of the surrounding box
    """
    rmax = spheres["r"].max()

    R_max = 0
    x_cm = spheres["x"].mean()
    y_cm = spheres["y"].mean()
    z_cm = spheres["z"].mean()
    for i in range(len(spheres)):
            d = np.sqrt((spheres["x"].iloc[i] - x_cm) ** 2 + (spheres["y"].iloc[i] - y_cm) ** 2 +\
                        (spheres["z"].iloc[i] - z_cm) ** 2) + spheres["r"].iloc[i]
            if (d > R_max):
                R_max = d
    R_max = R_max*fact
    xmin1, xmax1 = x_cm - R_max, x_cm + R_max
    ymin1, ymax1 = y_cm - R_max, y_cm + R_max
    zmin1, zmax1 = z_cm - R_max, z_cm + R_max
    
    return (xmin1, xmax1), (ymin1, ymax1), (zmin1, zmax1)

def mkgrid(xbounds, ybounds, zbounds, resolution):
    """
        compute dimensions of the surrounding box
    """
    xmin, xmax = xbounds
    ymin, ymax = ybounds
    zmin, zmax = zbounds

    # create a grid of the requested resolution
    x, y, z = np.mgrid[xmin:xmax:resolution*1j,
                       ymin:ymax:resolution*1j,
                       zmin:zmax:resolution*1j]

    return (x, y, z)

def middle_element(lst):
    if len(lst) % 2 != 0:
        return lst.index(range(lst) // 2)
    else:
        return len(lst) // 2 + len(lst) // 2 - 1