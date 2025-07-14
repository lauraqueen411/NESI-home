import pandas as pd
import matplotlib.pyplot as plt


def plot_summary(var,t,resample_interval):

    summary_df = pd.read_csv("/nesi/project/niwa00015/queenle/data/hydro_fingerprinting/model/d4PDF/summary_csv/"+var+"_1951-2021_" +resample_interval + "_trunc_" + str(t) + ".csv")

    for sort_type in ['nat_best','ant_best']:

        fig,axs = plt.subplots(2,2, figsize=(12,10))
        axs = axs.flatten()

        for i,s in enumerate(['summer','autumn','winter','spring']):

            sorted_df = summary_df[summary_df.season==s].sort_values(by=sort_type)

            axs[i].scatter([i for i in range(len(sorted_df.nat_upper))],sorted_df.nat_upper,c='blue',label='nat')
            axs[i].scatter([i for i in range(len(sorted_df.nat_lower))],sorted_df.nat_lower,c='blue',label='')
            axs[i].scatter([i for i in range(len(sorted_df.nat_best))],sorted_df.nat_best,c='blue',label='')

            axs[i].scatter([i for i in range(len(sorted_df.ant_upper))],sorted_df.ant_upper,c='red',label='ant')
            axs[i].scatter([i for i in range(len(sorted_df.ant_lower))],sorted_df.ant_lower,c='red',label='')
            axs[i].scatter([i for i in range(len(sorted_df.ant_best))],sorted_df.ant_best,c='red',label='')

            axs[i].vlines([i for i in range(len(sorted_df.nat_lower))],sorted_df.nat_lower,sorted_df.nat_upper,colors=['blue'],label='')
            axs[i].vlines([i for i in range(len(sorted_df.ant_lower))],sorted_df.ant_lower,sorted_df.ant_upper,colors=['red'],label='')

            axs[i].axhline(0,-0.5,1.5)
            axs[i].axhline(1,-0.5,1.5)

            axs[i].set_title(s + ', trunc = ' + str(t))
            
            axs[i].set_ylim(-3.2,4.5)

            axs[i].legend()

        plt.savefig('/nesi/project/niwa00015/queenle/plots/d4PDF/perfect_model/'+var+'/full/' + resample_interval + '/' + 'PM_ensemble_summary_'+sort_type+'_sort_highres_sharey.png',dpi=300)

        plt.close(fig)

for var in ['TA','ROF','PRECIPI']:
    t = 60
    resample_interval = 'annual'

    plot_summary(var,t,resample_interval)
