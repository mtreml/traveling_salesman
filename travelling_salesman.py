# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 18:45:28 2014

@author: michael
"""
import numpy as np
import matplotlib.pyplot as plt
import os
plt.close('all')

def roundtrip(route, N):
        
    c = route[1:N+1,:] - route[0:N,:]
    s = np.sum(np.sqrt(c[:,0]**2 + c[:,1]**2))
    
    return s
    
def distance(xy, a, b):
    
    c = xy[a,:] - xy[b,:]
    s = np.sum(np.sqrt(c[0]**2 + c[1]**2))
    
    return s

#### Read the list of airports and their GPS-coordinates ####
airports = open('airports', "r").read().split(',')
coordinates = open('coordinates', "r").read().split(';')
N = len(airports)
xy = np.zeros((N,2))
for j in range(N):
    xy[j,0] = coordinates[j].split(',')[0]  
    xy[j,1] = coordinates[j].split(',')[1]

#### Simulation parameters ####
L = N**2/4
K = 20
Tstart = 1
q = 1.05
route = np.concatenate((xy, np.reshape(xy[0,:], (1,2))))

#### Figure of the map ####
fig1 = plt.figure('Map')
plt.hold(True)
staedte, = plt.plot(xy[:,0],xy[:,1],'o')
for j in range(N):
    plt.annotate('{}'.format(airports[j]),
                         xy[j,:],
                         xytext=(-5, 5),
                         ha='right',
                         textcoords='offset points')
                         
start, = plt.plot(xy[0,0],xy[0,1], 'ro', label='Starting point')
random_route, = plt.plot(route[:,0], route[:,1],'--', label='Random route')# route
best_route, = plt.plot([],[], label='Optimized route')
plt.grid()
plt.ion()
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.get_current_fig_manager().window.raise_()
plt.show()
plt.xlabel('Longitude', fontsize = 10)
plt.ylabel('Latitude', fontsize = 10)
plt.title('Map of airports in the area of Botswana', fontsize = 15)

#### Figure of distance/costs ####
fig2 = plt.figure('Distance of roundtrip')
plt.grid()
plt.ion()
plt.hold(True)
plt.xlim(-0.5,K)
plt.xlabel('No of iterations', fontsize = 10)
plt.ylabel('Distance = Costs in arbitrary units', fontsize = 10)
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.get_current_fig_manager().window.raise_()
plt.show()
plt.title('Cost-optimization for route of a roundtrip', fontsize = 15)
files1 = []

# Simulated annealing loop
for k in range(K):
    count = 0
    E = roundtrip(route, N)    
    E_best = E
    E_mean_sum = 0
    E_var_sum = 0
    route_best = route
    if k == 0:
        T = Tstart
    else:
        T = Tstart/k**q
    
    for j in range(L):
        rands = np.sort(np.random.randint(1,N-1,2))
        a = rands[0]
        b = rands[1]
        s1 = distance(route, a-1, b)
        s2 = distance(route, a, b+1)
        s3 = distance(route, a-1, a)
        s4 = distance(route, b, b+1)
        E_neu = E + s1 + s2 - s3 - s4
        delta_E = E_neu - E
        p = np.min((1,np.exp(-delta_E/T)))
        
        cut = route[a:b+1,:]
        cuta = route[0:a,:]
        cutb = route[b+1::,:]
        route_neu = np.concatenate((cuta,np.flipud(cut),cutb))
        E_check = roundtrip(route_neu, N)
        
        if p == 1:
            route = route_neu
            E = E_neu
            count = count + 1
        else:
            r = np.random.rand(1)
            if p > r:
                route = route_neu
                E = E_neu
                count = count + 1
                
        # Computation of <E> and std(E)
        E_mean_sum = E_mean_sum + E
        E_mean = E_mean_sum/(j+1)
        E_var_sum = E_var_sum + (E_mean - E)**2
        if j>1:
            E_std = np.sqrt(E_var_sum/j)
            
        # Shortest route
        if E < E_best:
            E_best = E
            route_best = route
    
    cH = E_std**2/T**2
     
    plt.figure('Map');
    best_route.set_data(route_best[:,0], route_best[:,1])
    plt.pause(0.0000001)
    if k==0:
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5)
    
    # Save frames for gif generation
    fname1 = '_tmp_fig1%03d.png'%k
    print 'Saving frame', fname1
    fig1.savefig(fname1)
    files1.append(fname1)
      
    plt.figure('Distance of roundtrip');
    plt.errorbar(k,E_mean,E_std, marker='s', mfc='cyan', ecolor='b', label='Distance of roundtrip = Costs')
    plt.pause(0.0000001)
    if k==0:        
        E0 = E_mean;
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5) 
    
    acceptance = np.array(count)/np.array(L)   
    
plt.figure('Distance of roundtrip');
plt.plot(range(K+1), E0*np.ones(K+1), 'r--')
plt.plot(range(K+1), E_mean*np.ones(K+1), 'g--')
plt.annotate(str('Distance of random route: ' + str(round(E0,2))), (K/2, E0+1), xytext=None, textcoords=None)
plt.annotate(str('Distance of optimized route: ' + str(round(E_mean,2))), (K/2, E_mean+1), xytext=None, textcoords=None)
plt.annotate(str('Statistical route-optimization saves ' + str(round((E0 - E_mean)/E0*100,0)) + '% of costs!'), (K/4, E_mean + (E0-E_mean)/2), xytext=None, textcoords=None, size='xx-large',color='red')
print 'E_best = ' + str(round(E_best,2))
fig2.savefig('optimized-distance')
print 'Making movie animation - this may take a while.....'
os.system("convert -set delay 25 -colorspace RGB -colors 16 -dispose 1 -loop 0 -scale 50% _tmp* route-optimization.gif")
os.system("rm _tmp*")
print 'Done'