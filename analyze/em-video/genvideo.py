#!/usr/bin/env python3

# imports
from pathlib import Path
import subprocess
import os

from kuibit.simdir import SimDir
import matplotlib.pyplot as plt
from tqdm.auto import tqdm

# script dir
SCRIPT_DIR = Path(__file__).resolve().parent

# output settings
frames_dir = f"{SCRIPT_DIR}/snapshots"  # make the dir yourself
video_file = SCRIPT_DIR / "video.mp4"
fps = 21

# fetch data
sd = SimDir(f"{SCRIPT_DIR}/../../simulations/Merger_CCZ4_M=0.5,0.5-T=0.05,0.05-alpha=0,0.5pi-x0=8.001_h=3")
gf = sd.gf

Ey_x = gf.x["Ey"]
Ez_x = gf.x["Ez"]
By_x = gf.x["By"]
Bz_x = gf.x["Bz"]

# use Ey iterations as reference
iterations = Ey_x.available_iterations

# initialize plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True, gridspec_kw={"hspace": 0})

line_Ey, = ax1.plot([], [], color="C0", label=r"$x \times E_y$", marker=".", ms=2, lw=1)
line_Ez, = ax1.plot([], [], color="C9", label=r"$x \times E_z$", marker=".", ms=2, lw=1)

line_By, = ax2.plot([], [], color="C0", label=r"$x \times B_y$", marker=".", ms=2, lw=1)
line_Bz, = ax2.plot([], [], color="C9", label=r"$x \times B_z$", marker=".", ms=2, lw=1)

ax1.grid(alpha=0.5)
ax1.set_ylabel("Electric field")
ax1.set_ylim((-0.0015, 0.0015))  # manually set y axis limits
ax1.legend()

ax2.grid(alpha=0.5)
ax2.set_xlabel(r"$x$")
ax2.set_ylabel("Magnetic field")
ax2.set_ylim((-0.0015, 0.0015))  # manually set y axis limits
ax2.legend()

# I'm going to use the data from t = 0 to set x-axis limits
imin = 130
imax = -1
coor = Ey_x.get_iteration(0).get_level(0).grid.coordinates_1d[0]
coor = coor[imin:imax]
ax1.set_xlim((coor[0], coor[-1]))
ax2.set_xlim((coor[0], coor[-1]))

# iterate over all available time steps and save snapshots
for i, n in tqdm(enumerate(iterations), total=len(iterations), desc="Rendering frames"):
    Ey_it = Ey_x.get_iteration(n)
    Ez_it = Ez_x.get_iteration(n)
    By_it = By_x.get_iteration(n)
    Bz_it = Bz_x.get_iteration(n)

    Ey_lv = Ey_it.get_level(0)
    Ez_lv = Ez_it.get_level(0)
    By_lv = By_it.get_level(0)
    Bz_lv = Bz_it.get_level(0)

    Ey = Ey_lv.data
    Ez = Ez_lv.data
    By = By_lv.data
    Bz = Bz_lv.data

    coor = Ey_lv.grid.coordinates_1d[0]

    # crop data
    imin = 130
    imax = -1

    coor = coor[imin:imax]
    Ey = Ey[imin:imax]
    Ez = Ez[imin:imax]
    By = By[imin:imax]
    Bz = Bz[imin:imax]

    # update existing lines
    line_Ey.set_data(coor, coor * Ey)
    line_Ez.set_data(coor, coor * Ez)
    line_By.set_data(coor, coor * By)
    line_Bz.set_data(coor, coor * Bz)

    # update title with current simulation time
    fig.suptitle(f"$t = {Ey_it.time}$\n$(y=z=0)$")

    # save frame
    fig.savefig(f"{frames_dir}/frame_{i:06d}.png", bbox_inches="tight")

plt.close(fig)

# build video with ffmpeg
cmd = [
    "ffmpeg",
    "-y",
    "-framerate",
    f"{fps}",
    "-i",
    f"{frames_dir}/frame_%06d.png",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv444p",
    "-crf",
    "18",
    "-preset",
    "medium",
    f"{video_file}",
]

subprocess.run(cmd, check=True)
