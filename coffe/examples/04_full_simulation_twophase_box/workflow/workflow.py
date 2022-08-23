
import os
from coffe.gmx import sim, simgen, boxes
from coffe.core import cluster

# prepare output folder
try:
    os.mkdir("../output_workflow")
except Exception:
    pass

generator = simgen.GmxChainGenerator(cfg_file="workflow.cfg", section="generator")

gro, top = boxes.gmx_mkbox_twophase(cfg_file="workflow.cfg", section=system)
chain = generator.generate("../output_workflow/output_{}".format(system), gro, top)
job = cluster.ClusterJob(cfg_file="workflow.cfg", section="cluster", job_name=system)
job += chain
job_id = job.submit()
print("Submitted job {}; status: {}".format(job_id, job.status))
