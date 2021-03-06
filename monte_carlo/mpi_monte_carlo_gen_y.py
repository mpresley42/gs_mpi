print "I exist"
from mpi4py import MPI 
import sys, os
import aipy as a, numpy as n, pylab as p
import capo as C
import basic_amp_aa_grid_gauss as agg
import useful_functions as uf
import matplotlib as mpl
print "imported everything"

def haslam_extrap(hasdat=None,fq=0.1):
    alf0=2.8; var = 0.1 # from table on page 4 of http://arxiv.org/pdf/1106.0007.pdf
    if hasdat==None:
        hasmap = a.map.Map(fromfits='/global/homes/m/mpresley/scripts/general_files/fits_files/haslam408_32.fits')
        hasdat = hasmap.map.map 
    alf = n.random.randn(hasdat.shape[0])*var
    fqdat = hasdat*(fq/0.408)**(alf-alf0) 
    return fqdat

def generate_sky_model_y(baselines,beam_sig,gsm_map=None,gsm_data_file=None):
    """
    y is a vector of the visibilities at different baselines
    """
    if gsm_data_file!=None:
        healmap = a.map.Map(fromfits=gsm_data_file)
    elif gsm_map!=None:
        healmap = a.map.Map()
        healmap.set_map(gsm_map)
    else:
        return None

    px_array = n.arange(healmap.npix()) # gets an array of healpix pixel indices
    rx,ry,rz = n.array(healmap.px2crd(px_array,ncrd=3)) # finds the topocentric coords for each healpix pixel
    phi,theta = n.array(healmap.px2crd(px_array,ncrd=2)) # phi,theta in math coords
    true_sky = healmap.map.map
    amp = uf.gaussian(beam_sig,n.zeros_like(theta),phi)
    dOmega = 4*n.pi/px_array.shape[0]

    visibilities = n.zeros(baselines.shape[0],dtype='complex')
    for kk in range(baselines.shape[0]):
        bx,by,bz = baselines[kk]
        Vis = amp*true_sky*n.exp(2j*n.pi*(bx*rx+by*ry+bz*rz))*dOmega
        visibilities[kk] = n.sum(Vis)
    return visibilities


# define mpi parameters
comm = MPI.COMM_WORLD
rank = comm.Get_rank() #int associated with each processor. ranges from 0 to number of processors
size=comm.Get_size()
master = 0
num_slaves = size-1
print "defined mpi params"

# define parameters related to calculation 
hasmap = a.map.Map(fromfits='/global/homes/m/mpresley/scripts/general_files/fits_files/haslam408_32.fits')

_,num0,beam_sig,del_bl,num_bl = sys.argv
num0=int(num0);beam_sig=float(beam_sig); del_bl=float(del_bl); num_bl=int(num_bl)
baselines = agg.make_pos_array(del_bl,num_bl)

save_interval = 10000
save_num = 0
savekey = 'grid_del_bl_{0:.2f}_num_bl_{1}_beam_sig_{2:.2f}_'.format(del_bl,num_bl,beam_sig)

print "defined hasmap stuff"

# define parameters related to task-mastering
num1 = baselines.shape[0]
numToDo = num0
num_sent = 0 # this functions both as a record of how many assignments have 
             # been sent and as a tag marking which matrix entry was calculated
num_recv = 0


print "defined task-mastering stuff"

# Big running loop
# If I am the master process
if rank==master:
    print "I am the master! Muahaha!"
    if savekey not in os.listdir('/global/homes/m/mpresley/scripts/monte_carlo/'):
        os.mkdir('/global/homes/m/mpresley/scripts/monte_carlo/{0}'.format(savekey))
    # send out first round of assignments
    for kk in range(num_slaves):
        selectedi = num_sent
        print "num_sent = ",num_sent
        comm.send(selectedi,dest=kk+1)
        print "i = ",selectedi," was sent to slave ",kk+1
        num_sent +=1
    print "Master sent out first round of assignments"
    # listen for results and send out new assignments
    for kk in range(numToDo):
        source,entry = comm.recv(source=MPI.ANY_SOURCE)
        selectedi = comm.recv(source=source)
        # stick entry into matrix 
        print 'entry ',entry.shape
        if num_recv%save_interval==0:
            matrix = entry
        else:
            matrix = n.vstack((matrix,entry))
        print 'Master just received element (i,) = ',selectedi,' from slave ',source
        # if there are more things to do, send out another assignment
        if num_sent<numToDo:
            selectedi = num_sent
            comm.send(selectedi,dest=source)
            print "Master sent out i = ",selectedi,' to slave ',source
            num_sent +=1
        else:
            # send a -1 to tell slave that task is complete
            comm.send(-1,dest=source)
            print "Master sent out the finished i to slave ",source
        if num_recv%save_interval==save_interval-1:
            n.savez_compressed('/global/homes/m/mpresley/scripts/monte_carlo/{0}/mc_{1}'.format(savekey,save_num),matrix=matrix)
            matrix=None
            save_num+=1
        num_recv += 1

# If I am a slave and there are not more slaves than jobs
elif rank<=numToDo:
    print "I am slave ",rank
    complete = False
    while not complete:
        # Get assignment
        selectedi = comm.recv(source=master)
        print "slave ",rank," just recieved i = ",selectedi
        if selectedi==-1:
            # if there are no more jobs
            complete=True
            print "slave ",rank," acknoledges job completion"
        else:
            # compute the matrix element
            gsm_map = haslam_extrap(hasdat=hasmap.map.map)
            element = generate_sky_model_y(baselines,beam_sig,gsm_map=gsm_map)
            # send answer back
            comm.send((rank,element),dest=master)
            comm.send(selectedi,dest=master)
            print "Slave ",rank," sent back i = ",selectedi
comm.Barrier()

# if rank==master:
#     print "The master will now save the matrix."
#     n.savez_compressed('/global/homes/m/mpresley/scripts/monte_carlo/matrices/monte_carlo_{0}_'.format(savekey),matrix=matrix)
#     print matrix.shape

MPI.Finalize()



