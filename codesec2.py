import pandas as pd
import gurobipy as gp
import numpy as np
from gurobipy import GRB
model = gp.Model("NAFTAL")
Distance=pd.read_excel("distance.xlsx")
xcord=np.array(Distance["XCORD"])
ycord=np.array(Distance["YCORD"])
N=len(ycord)
C=[30000,30000,30000]

ccost=2 #: the cost of traveling one unit distance of distance.
K=7 # number of identical vehicles
"""
𝑐𝑘: the cost of activating the vehicle k ∈ 𝐾
"""
ck=[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]

d=np.zeros([N,N])#the distance between two different customers i and j.

for i in range(N):
    for j in range(N):
        d[i][j]=((xcord[i]-xcord[j])**2+(ycord[i]-ycord[j])**2)**(1/2)

e=np.array(Distance["EARLIEST TIME"])#earliest service time start time of customer i.
l=np.array(Distance["LATEST TIME"])#: latest service start time of customer i.
Pmax=0.7
Ce=[1.2,1.2,1.2,1.2,1.2,1.2,1.2,1.2,1.2,1.2,
    1.2,1.2,1.2,1.2,1.2,1.2,1.2,1.2,1.2,1.2]#the unit penalty for the service that begins before its earliest start time
Cl=[2,2,2,2,2,2,2,2,2,2,
    2,2,2,2,2,2,2,2,2,2]# the unit penalty for the service that begins after its latest start time
q=np.array(Distance.iloc[:,4:7])
t=d/2 # the travel time between two different customers i and j.
u=np.array(Distance["SERVICE TIME (hr)"])
bigM=100000000


x= model.addVars(N,N,K,vtype=GRB.BINARY, name="x")
z=model.addVars(K,vtype=GRB.BINARY, name="z")
s=model.addVars(N,vtype=GRB.CONTINUOUS ,name="s")
y=model.addVars(N,vtype=GRB.CONTINUOUS ,name="y")#Variable that prevents subtours from occurring
deltai=model.addVars(N,vtype=GRB.CONTINUOUS ,name="deltai")
deltal=model.addVars(N,vtype=GRB.CONTINUOUS ,name="deltal")


constraint1= model.addConstrs( gp.quicksum(x[i,0,k] for i in range(1,N))==1 for k in range(K) ) 
constraint2= model.addConstrs( gp.quicksum(x[0,i,k] for i in range(1,N))==1 for k in range(K) ) 
constraint3= model.addConstrs( gp.quicksum(x[i,j,k] for i in range(0,N)for k in range(K) )==1 for j in range(1,N) if i!=j) 
constraint4= model.addConstrs( gp.quicksum(x[i,j,k] for j in range(0,N)for k in range(K) )==1 for i in range(1,N))
constraint5= model.addConstrs( gp.quicksum(x[i,m,k] for i in range(0,N))-  gp.quicksum(x[m,j,k] for j in range(0,N))==0 for m in range(1,N) for k in range(K))
constraint6= model.addConstrs( gp.quicksum(q[i][n]*x[i,j,k]for i in range(0,N) for j in range(0,N)) <=C[n] for k in range(K) for n in range(3) )
constraint7=model.addConstrs(s[i]-e[i]+Pmax>=0 for i in range(1,N))
constraint8=model.addConstrs(s[i]-l[i]-Pmax<=0 for i in range(1,N))
constraint9=model.addConstrs(gp.quicksum(x[i,j,k]*(s[i]+u[i]+t[i][j])for i in range(0,N) for k in range(K))==s[j] for j in range(1,N))
constraintadd1=model.addConstr(s[0]==e[0])
constraint10=model.addConstrs(deltai[i]>=e[i]-s[i] for i in range(1,N))
constraint11=model.addConstrs(deltal[i]>=s[i]-l[i] for i in range(1,N))
constraintadd2=model.addConstrs(y[j]>=y[i]+1-N*(1- gp.quicksum(x[i,j,k] for k in range(K) ))for i in range(1,N) for j in range(1,N) )
constraintadd3=model.addConstrs(gp.quicksum(x[i,j,k]  for i in range(0,N) for j in range(0,N))<=z[k]*bigM for k in range(K))

model.setObjective(gp.quicksum(ccost*d[i][j]*x[i,j,k] for i in range(0,N) for j in range(0,N) for k in range(K))+gp.quicksum(ck[k]*z[k]for k in range(K))+
                  gp.quicksum(Ce[i]*deltai[i]+Cl[i]*deltal[i] for i in range(1,N)) ,GRB.MINIMIZE)
model.write("NAFTAL.lp")
model.optimize()

for i range(N):
    for j range(N):
        for k range(K):
            if x[i,j,k].x> 0:
                print(f"\n  {x[i,j,k]} ."),
obj = model.getObjective()
print(obj.getValue())