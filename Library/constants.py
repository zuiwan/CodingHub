#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pytz import timezone

DOCKER_PRE = "registry.cn-shanghai.aliyuncs.com/russellcloud/"

DOCKER_IMAGES = {
    "cpu": {
        "tensorflow": "tensorflow:latest-py3",
        "tensorflow:py2": "tensorflow:latest-py2",
        "tensorflow-1.0": "tensorflow:1.0.0-py3",
        "tensorflow-1.0:py2": "tensorflow:1.0.0-py2",
        "theano": "theano:latest-py3",
        "theano:py2": "theano:latest-py2",
        "keras": "tensorflow:latest-py3",
        "keras:py2": "tensorflow:latest-py2",
        "caffe": "caffe:latest-py3",
        "caffe:py2": "caffe:latest-py2",
        "torch": "torch:latest-py3",
        "torch:py2": "torch:latest-py2",
        "pytorch": "pytorch:latest-py3",
        "pytorch:py2": "pytorch:latest-py2",
        "chainer": "chainer:latest-py3",
        "chainer:py2": "chainer:latest-py2",
        "mxnet:py2": "mxnet:latest-py2",
        "kur": "kur:latest-py3",
    },
    "gpu": {
        "tensorflow": "tensorflow:latest-gpu-py3",
        "tensorflow:py2": "tensorflow:latest-gpu-py2",
        "tensorflow-1.0": "tensorflow:1.0.0-gpu-py3",
        "tensorflow-1.0:py2": "tensorflow:1.0.0-gpu-py2",
        "theano": "theano:latest-gpu-py3",
        "theano:py2": "theano:latest-gpu-py2",
        "keras": "tensorflow:latest-gpu-py3",
        "keras:py2": "tensorflow:latest-gpu-py2",
        "caffe": "caffe:latest-gpu-py3",
        "caffe:py2": "caffe:latest-gpu-py2",
        "torch": "torch:latest-gpu-py3",
        "torch:py2": "torch:latest-gpu-py2",
        "pytorch": "pytorch:latest-gpu-py3",
        "pytorch:py2": "pytorch:latest-gpu-py2",
        "chainer": "chainer:latest-gpu-py3",
        "chainer:py2": "chainer:latest-gpu-py2",
        "mxnet:py2": "mxnet:latest-gpu-py2",
        "kur": "kur:latest-gpu-py3",
    }
}

DEFAULT_DOCKER_IMAGE = "tensorflow:latest-py3"

DEFAULT_ENV = "keras"


PST_TIMEZONE = timezone("America/Los_Angeles")

DEFAULT_FLOYD_IGNORE_LIST = """
# Directories to ignore when uploading code to floyd
# Do not add a trailing slash for directories

.git
.eggs
eggs
lib
lib64
parts
sdist
var
"""

CPU_INSTANCE_TYPE = "cpu_high"
GPU_INSTANCE_TYPE = "gpu_high"

FIRST_STEPS_DOC = """
Start by cloning the sample project
    git clone https://github.com/tensorflow-examples.git
    cd tensorflow-examples

And init a floyd project inside that.
    floyd init --project example-proj
"""

# SimCity4 Loading messages
# https://www.gamefaqs.com/pc/561176-simcity-4/faqs/22135
# Credits: EA Games
LOADING_MESSAGES = [
    "Adding Hidden Layers",
    "Adjusting Bell Curves",
    "Aesthesizing Industrial Grade Containers",
    "Aligning Covariance Matrices",
    "Applying Feng Shui Backprops",
    "Applying Theano Soda Layer",
    "Asserting Packed Exemplars",
    "Attempting to Lock Back-Buffer",
    "Binding Sampling Root System",
    "Breeding Neural Nets",
    "Building Deep Data Trees",
    "Bureacritizing Deep Learning Bureaucracies",
    "Calculating Inverse Probability Matrices",
    "Calculating SGD Expectoration Trajectory",
    "Calibrating Blue Skies",
    "Charging Ozone Layer",
    "Coalescing Cloud Formations",
    "Cohorting Exemplars",
    "Collecting Meteor Particles",
    "Compounding Inert Tessellations",
    "Compressing Fish Files",
    "Computing Optimal Bin Packing",
    "Concatenating Sub-Contractors",
    "Containing Existential Buffer",
    "Debarking Ark Ramp",
    "Debunching Unionized Commercial Services",
    "Deciding What Message to Display Next",
    "Decomposing Singular Values",
    "Decrementing Tectonic Plates",
    "Deleting Ferry Routes",
    "Depixelating Inner Mountain Surface Back Faces",
    "Depositing Slush Funds",
    "Destabilizing Economic Indicators",
    "Determining Width of Blast Fronts",
    "Deunionizing Bulldozers",
    "Dicing Trained Models",
    "Diluting Livestock Nutrition Variables",
    "Downloading Satellite Terrain Data",
    "Exposing Flash Variables to Streak System",
    "Extracting Gradient Resources",
    "Factoring Pay Scale",
    "Fixing Election Outcome Matrix",
    "Flood-Filling Ground Water",
    "Flushing Pipe Network",
    "Gathering Particle Sources",
    "Generating Scheduled Jobs",
    "Gesticulating Mimes",
    "Graphing Container Migration",
    "Hiding Willio Webnet Mask",
    "Implementing Impeachment Routine",
    "Increasing Accuracy of RCI Simulators",
    "Increasing Neural Magmafacation",
    "Initializing My Sim Tracking Mechanism",
    "Initializing CNN Timetable",
    "Initializing Robotic Click-Path AI",
    "Inserting Sublimated Messages",
    "Integrating Multidimensional Curves",
    "Integrating Illumination Form Factors",
    "Integrating Population Graphs",
    "Iterating Cellular Automata",
    "Lecturing Errant Subsystems",
    "Mixing Dropouts in Genetic Pool",
    "Modeling Object Components",
    "Mopping Occupant Leaks",
    "Normalizing Power",
    "Obfuscating Quigley Matrix",
    "Overconstraining Dirty Industry Calculations",
    "Partitioning City Grid Singularities",
    "Perturbing Matrices",
    "Pixalating Overfitting Patches",
    "Polishing Water Highlights",
    "Populating Lot Templates",
    "Preparing Sprites for Random Walks",
    "Prioritizing Landmarks",
    "Projecting Law Enforcement Pastry Intake",
    "Realigning Alternate Time Frames",
    "Reconfiguring User Mental Processes",
    "Relaxing Splines",
    "Removing Road Network Speed Bumps",
    "Removing Texture Gradients",
    "Removing Vehicle Avoidance Behavior",
    "Resolving GUID Conflict",
    "Reticulating Splines",
    "Retracting Phong Shader",
    "Retrieving from Back Store",
    "Reverse Engineering Image Consultant",
    "Routing Neural Network Infanstructure",
    "Scrubbing Terrain",
    "Searching for Llamas",
    "Seeding Architecture Simulation Parameters",
    "Sequencing Particles",
    "Setting Advisor Moods",
    "Setting Inner Deity Indicators",
    "Setting Universal Physical Constants",
    "Sonically Enhancing Occupant-Free Timber",
    "Speculating Stock Market Indices",
    "Splatting Transforms",
    "Stratifying Ground Layers",
    "Sub-Sampling Water Data",
    "Synthesizing Gravity",
    "Synthesizing Wavelets",
    "Time-Compressing Simulator Clock",
    "Unable to Reveal Current Activity",
    "Weathering Buildings",
    "Zeroing Crime Network"
]


# numerical value
SQL_LIMIT_HIGH = 18446744073709551615L


# text
CPU_INSTANCE_TYPE = "cpu_high"
GPU_INSTANCE_TYPE = "gpu_high"

routing_dict = {GPU_INSTANCE_TYPE: 'task.user.compute.gpu', CPU_INSTANCE_TYPE: 'task.user.compute.cpu'}
queue_dict = {GPU_INSTANCE_TYPE: 'gpu', CPU_INSTANCE_TYPE: 'cpu'}

k_log_output_1 = "Task submitted successfully, queued for processing"
k_log_output_2 = "Task start to be executed..."
k_log_output_3 = "mkdir output"
k_log_output_4 = "default_env: {}, image: {} ."
k_log_output_5 = "work_volume create successfully, mount dir: {}"
k_log_output_6 = "data_volume create successfully, data_id: {}, mount dir: {}"
k_log_output_7 = "Task create successfully"
k_log_output_8 = "Task is running now ~"
k_log_output_9 = "Waiting for Task to complete ~"
k_log_output_10 = "Export output dir to create new dataset : ************"
k_log_output_11 = "[{}] Finishing execution in {} seconds for Task"
