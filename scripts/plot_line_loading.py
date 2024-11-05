import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pypsa
from matplotlib.colors import Normalize
from plot_power_network import load_projection

def get_dc_lines(n):
    neglect_link = n.links.query("carrier != 'DC'").index

    links_t_p0 = n.links_t.p0.copy()
    links_t_p0.loc[:, neglect_link] = 0

    links_p_nom_opt = n.links.p_nom_opt.copy()
    links_p_nom_opt[neglect_link] = 0

    return links_t_p0, links_p_nom_opt

if __name__ == "__main__":
    if "snakemake" not in globals():
        from _helpers import mock_snakemake

        snakemake = mock_snakemake("plot_line_loading")

    n = pypsa.Network(snakemake.input.network)

    # Get each value of lines and links loading
    loading_line = abs(n.lines_t.p0) / n.lines.s_nom_opt
    loading_line_ave = loading_line.mean() * 100

    links_t_p0, links_p_nom_opt = get_dc_lines(n)
    loading_link = abs(links_t_p0) / links_p_nom_opt
    loading_link = loading_link.fillna(0)
    loading_link_ave = loading_link.mean() * 100

    # Get weighted average value of Lines and Links
    line_weight = pd.DataFrame(index=loading_line.columns)

    line_weight["by_cap"] = [n.lines.s_nom_opt[i] / n.lines.s_nom_opt.sum() for i in line_weight.index]
    line_weight["by_cap_length"] = [n.lines.s_nom_opt[i] * n.lines.length[i] / (n.lines.s_nom_opt * n.lines.length).sum() for i in line_weight.index]
    loading_line_ave_all = round(sum(line_weight["by_cap_length"] * loading_line_ave),1)

    link_weight = pd.DataFrame(index=n.links.index)

    link_weight["by_cap"] = [links_p_nom_opt[i] / links_p_nom_opt.sum() for i in link_weight.index]
    link_weight["by_cap_length"] = [links_p_nom_opt[i] * n.links.length[i] / (links_p_nom_opt * n.links.length).sum() for i in link_weight.index]
    loading_link_ave_all = round(sum(link_weight["by_cap_length"] * loading_link_ave),1)

    # Plotting map
    loading_link_alpha = pd.Series(index=n.links.index)
    loading_link_alpha[n.links.query("carrier != 'DC'").index] = 0
    loading_link_alpha = loading_link_alpha.fillna(1)

    proj = load_projection(snakemake.params.plotting)

    map_opts = snakemake.params.plotting["map"]

    if map_opts["boundaries"] is None:
        map_opts["boundaries"] = regions.total_bounds[[0, 2, 1, 3]] + [-1, 1, -1, 1]

    fig, ax = plt.subplots(subplot_kw={"projection": proj}, figsize=(10, 10))
    norm = Normalize(vmin=0, vmax=100, clip=True)

    collection = n.plot(
        ax=ax,
        line_colors=loading_line_ave,
        line_cmap=plt.cm.jet,
        line_norm=norm,
        link_colors=loading_link_ave,
        link_cmap=plt.cm.jet,
        link_alpha=loading_link_alpha,
        link_norm=norm,
        title="Line loading",
        bus_sizes=1e-3,
        bus_alpha=0.7,
        boundaries=map_opts["boundaries"]
    )

    ax.set_title(f'Average AC line loading: {loading_line_ave_all} %\nAverage DC link loading: {loading_link_ave_all} %', 
                loc='left', 
                x=0.02, 
                y=0.90,
                fontsize=12
                )

    plt.colorbar(collection[1], label="line loading [%]", ax=ax)

    