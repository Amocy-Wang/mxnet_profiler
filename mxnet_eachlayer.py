# Only support: endsign is unique name in the whole network.
import numpy as np
import os
import sys
import numpy
import json
import datetime

mxnet_profile = sys.argv[1]
startsign = sys.argv[2]
endsign = sys.argv[3]

with open(mxnet_profile) as data_file:
  data = json.load(data_file)

all_layers = data["traceEvents"]
buf_name = []
buf_ts = []
start = 0
end = 2
all_time = []

for idx_l in range(len(all_layers)):
  thislayer = all_layers[idx_l]
  layername = thislayer["name"]
  # layer in network.
  if layername == '['+startsign+']' and start == 0 and end == 2:
    start = 1
    end = 0
    buf_name = []
    buf_ts = []
  if layername[0] == '[' and start == 1 and end == 0:
    thisname = layername.lstrip('[').rstrip(']')
    timestamp = thislayer["ts"]
    buf_name.append(thisname)
    buf_ts.append(timestamp)
    # sign for the last layer profiling data in profile file
    if layername == '['+endsign+']':
      end = 1
      continue
  if layername == '['+endsign+']' and end == 1:
    thisname = layername.lstrip('[').rstrip(']')
    timestamp = thislayer["ts"]
    buf_name.append(thisname)
    buf_ts.append(timestamp)
    end = 2
    start = 0
    endts_list = [datetime.datetime.utcfromtimestamp(buf_ts[idx_end]) for idx_end in range(len(buf_ts)) if idx_end % 2 == 1]
    startts_list = [datetime.datetime.utcfromtimestamp(buf_ts[idx_start]) for idx_start in range(len(buf_ts)) if idx_start % 2 == 0]
    # calculate wall duration based on timestamp
    wallduration = [((endts_list[idx_time] - startts_list[idx_time]).total_seconds()) / 1000.0 for idx_time in range(len(endts_list))]
    print wallduration
    all_time.append(wallduration)

all_time = np.asarray(all_time)
all_time = np.mean(all_time, axis=0)
layers = [buf_name[filt] for filt in range(len(buf_name)) if filt % 2 == 0]
print len(layers)
print len(all_time)

out_file = "eachlayer_" + mxnet_profile.split('.')[0] + '.csv'
out = open(out_file, 'w')
for cnt_out in range(len(layers)):
  out.write(layers[cnt_out] + ' ') 
  out.write(str(all_time[cnt_out]) + '\n') 
    

  
