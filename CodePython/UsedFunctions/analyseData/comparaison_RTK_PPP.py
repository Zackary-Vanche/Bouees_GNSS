import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from open_kin import *
from datetime import datetime, timedelta
from scipy.stats import iqr
import seaborn as sns 

sns.set_theme()
SURCHARGE_OCEANO = True
if SURCHARGE_OCEANO:
    SURCHARGE_OCEANO_LABEL = 'surcharge_oceano'
else:
    SURCHARGE_OCEANO_LABEL = 'no_surcharge_oceano'

## Marégraphe ## 
FILE_MAREGRAPHE_BARRAGE = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\maregraphe_barrage\data_maregraphe_radar_barrage_Fevrier2023.csv"

## Boueé LIENSs RTK ## 
# Geod + time
FILE_LIENSS_RTK_ITRF14_TIME = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_RTK\Time-Map-data-2023-02-09 12_13_12_ITRF14.csv"
# Geocentrique
FILE_LIENSS_RTK_ITR14_GEO = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_RTK\Map-data-2023-02-09 12_13_12_ITRF14_Geocentrique.csv"

## Bouée ENSTA Pride PPP ##
if SURCHARGE_OCEANO:
    # Après correction du 21/02/2023 (nouveau traitement PPP)
    FILE_BOUEE_PPP_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_Bouee_PPP_corr_21022023\kin_2023039_boue_Bouee2"
else:
    # Avant correction du 21/02/2023
    FILE_BOUEE_PPP_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_Bouee_PPP\kin_2023039_boue_Bouee2"


## Bouée ENSTA PPP NRCAN ##
FILE_BOUEE_NRCAN_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_Bouée_PPPNRCAN\BoueeENSTA_002_BOUE00FRA_R_20230391100_02D_01S_MO_full_output\BOUE00FRA_R_20230391100_02D_01S_MO.pos"

## Bouée LIENSs Pride PPP ##
if SURCHARGE_OCEANO:
    # Après correction du 21/02/2023 (nouveau traitement PPP)
    FILE_LIENSS_PPP_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_Bouee_PPP_corr_21022023\kin_2023039_boue_LIENSs"
else:
    # Avant correction du 21/02/2023
    FILE_LIENSS_PPP_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_Bouee_PPP\kin_2023039_boue_LIENSs"

## Bouée LIENSs PPP NRCAN ##
FILE_LIENSS_NRCAN_ITRF14 = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\data_2022_2023\Semaine2\LIENSS_Bouée_PPPNRCAN\LIENSs_001_BOUE00FRA_R_20230390846_27H_01S_MO_full_output\BOUE00FRA_R_20230390846_27H_01S_MO.pos"


if SURCHARGE_OCEANO:
    FOLDER_SAVE = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Rapport\Analyse\Surchage_Oceano"
else:
    FOLDER_SAVE = r"C:\Users\33686\Desktop\ENSTAB\Cours\3A\Guerledan\Rapport\Analyse\No_Surchage_Oceano" 
    
FILE_RESULT = FOLDER_SAVE + f'\\resultat_analyse_{SURCHARGE_OCEANO_LABEL}.txt'

lines_result = []
header = ['#####################################################\n',
          'Bouée LIENSs:\n',
          f'\tPosition PPP (ITRF14): {FILE_LIENSS_PPP_ITRF14}\n',
          f'\tPosition RTK (ITRF14): {FILE_LIENSS_RTK_ITRF14_TIME}\n',
          'Bouée ENSTA:\n',
          f'\tPosition PPP (ITRF14): {FILE_BOUEE_PPP_ITRF14}\n',
          'Marégraphe barrage EDF: \n', 
          f'\tHauteur ellipsoïdale: {FILE_MAREGRAPHE_BARRAGE}\n',
          f'Surcharge océano: {SURCHARGE_OCEANO}\n' 
          '#####################################################\n\n']

lines_result += header

# N_GEOID = +49.428 # Ondulation du géoid RGF93
N_GEOID = +49.445 # Ondulation du géoid ITRF14

OFFSET_JD = 2400000.5 # Offset to convert MJD into JD 
LIENSS_TIRANT_DAIR = (20 - 5) * 1e-2 
BOUEE_TIRANT_DAIR = 22.5 * 1e-2
FIGURE_SIZE = (16, 8)

def loadNRCAN_pos(file, tirant_dair):
    df = pd.read_csv(file, delim_whitespace=True, skiprows=5)
    time = pd.to_datetime(df['YEAR-MM-DD'] + ' ' + df['HR:MN:SS.SS'])
    df['time'] = time
    df = df.rename(columns={"HGT(m)": "Height"})
    df['Surface_Height'] = df.Height - tirant_dair
    return df

pos_LIENSs_PPP = open_buoy(FILE_LIENSS_PPP_ITRF14)
pos_LIENSs_PPP['Jd'] = pos_LIENSs_PPP.Mjd + OFFSET_JD
pos_LIENSs_PPP['time'] = pd.to_datetime(pos_LIENSs_PPP.Jd, origin='julian', unit='D') + pd.Series([timedelta(seconds=s) for s in pos_LIENSs_PPP.Sod])
pos_LIENSs_PPP['Surface_Height'] = pos_LIENSs_PPP.Height - LIENSS_TIRANT_DAIR

pos_LIENSs_RTK = pd.read_csv(FILE_LIENSS_RTK_ITRF14_TIME, delimiter=',')
pos_LIENSs_RTK['time'] = pd.to_datetime(pos_LIENSs_RTK['time'])
pos_LIENSs_RTK['Surface_Height'] = pos_LIENSs_RTK.Height - LIENSS_TIRANT_DAIR
# pos_LIENSs_RTK['Surface_Height'] = pos_LIENSs_RTK.Height 

pos_LIENSs_RTK_geo = pd.read_csv(FILE_LIENSS_RTK_ITR14_GEO, delimiter=',', skiprows=15, names=['X', 'Y', 'Z'], usecols=[1, 2, 3])
pos_LIENSs_RTK['X'] = pos_LIENSs_RTK_geo.X
pos_LIENSs_RTK['Y'] = pos_LIENSs_RTK_geo.Y
pos_LIENSs_RTK['Z'] = pos_LIENSs_RTK_geo.Z

# NRCAN
pos_LIENSs_NRCAN = loadNRCAN_pos(FILE_LIENSS_NRCAN_ITRF14, LIENSS_TIRANT_DAIR)

pos_Bouee2 = open_buoy(FILE_BOUEE_PPP_ITRF14)
pos_Bouee2['Jd'] = pos_Bouee2.Mjd + OFFSET_JD
pos_Bouee2['time'] = pd.to_datetime(pos_Bouee2.Jd, origin='julian', unit='D') + pd.Series([timedelta(seconds=s) for s in pos_Bouee2.Sod])
pos_Bouee2['Surface_Height'] = pos_Bouee2.Height - BOUEE_TIRANT_DAIR

pos_Bouee2_NRCAN = loadNRCAN_pos(FILE_BOUEE_NRCAN_ITRF14, BOUEE_TIRANT_DAIR)
                   
maregraphe_barrage = pd.read_csv(FILE_MAREGRAPHE_BARRAGE, delimiter=';', names=['time', 'altitude'])
maregraphe_barrage.time = pd.to_datetime(maregraphe_barrage.time )
maregraphe_barrage['Surface_Height'] = maregraphe_barrage.altitude + N_GEOID

# Subset valide period 
fmt = '%Y-%m-%d %H:%M:%S'
start = datetime.strptime('2023-02-08 12:00:00', fmt)
stop = datetime.strptime('2023-02-09 10:00:00', fmt)

pos_LIENSs_PPP = pos_LIENSs_PPP.loc[(pos_LIENSs_PPP.time >= start) & (pos_LIENSs_PPP.time <= stop)]
pos_LIENSs_RTK = pos_LIENSs_RTK.loc[(pos_LIENSs_RTK.time >= start) & (pos_LIENSs_RTK.time <= stop)]
pos_Bouee2 = pos_Bouee2.loc[(pos_Bouee2.time >= start) &(pos_Bouee2.time <= stop)]
maregraphe_barrage = maregraphe_barrage.loc[(maregraphe_barrage.time >= start) &(maregraphe_barrage.time <= stop)]
pos_Bouee2_NRCAN = pos_Bouee2_NRCAN.loc[(pos_Bouee2_NRCAN.time >= start) & (pos_Bouee2_NRCAN.time <= stop)]
pos_LIENSs_NRCAN = pos_LIENSs_NRCAN.loc[(pos_LIENSs_NRCAN.time >= start) & (pos_LIENSs_NRCAN.time <= stop)]

# dic_buoys = {'LIENSs PPP': pos_LIENSs_PPP, 'LIENSs RTK': pos_LIENSs_RTK, 'LIENSs NRCAN': pos_LIENSs_NRCAN, 
#              'Bouée ENSTA NRCAN': pos_Bouee2_NRCAN, 'Bouée ENSTA PPP': pos_Bouee2, 'Marégraphe barrage': maregraphe_barrage}

pos_LIENSs_RTK.Surface_Height[pos_LIENSs_RTK.metric == 'LIENSS2_nofix'] = np.nan
pos_LIENSs_RTK = pos_LIENSs_RTK.dropna()
pos_LIENSs_RTK.Longitude = pos_LIENSs_RTK.Longitude.astype(float)
pos_LIENSs_RTK.Latitude = pos_LIENSs_RTK.Latitude.astype(float)

pos_LIENSs_RTK.time -= timedelta(minutes=59, seconds=41)
dic_buoys = {'LIENSs PPP cinématique': pos_LIENSs_PPP, 'LIENSs RTK': pos_LIENSs_RTK, 'Bouée ENSTA PPP cinématique': pos_Bouee2, 'Marégraphe barrage': maregraphe_barrage}

# Analyse de la composante z
# plt.figure()
# for buoy_name in dic_buoys.keys():
#     buoy = dic_buoys[buoy_name]
#     plt.plot(buoy.time, buoy.Surface_Height, label=buoy_name)
    
# plt.xticks(rotation=20)
# plt.xlabel('Date')
# plt.ylabel('Hauteur ellipsoïdale [m]')
# plt.legend()
# plt.title('Composante verticale')
# plt.tight_layout()
# plt.savefig(f"{FOLDER_SAVE}\\Comparaison_z_{SURCHARGE_OCEANO_LABEL}.png")

# Analyse de la composante z pour les données ou le fix RTK est good


plt.figure()
for buoy_name in dic_buoys.keys():
    buoy = dic_buoys[buoy_name]
    if buoy_name == 'Marégraphe barrage':
        plt.scatter(buoy.time, buoy.Surface_Height, label=buoy_name, color=sns.color_palette()[3], marker="^")
    else:
        plt.plot(buoy.time, buoy.Surface_Height, label=buoy_name)

# fill_1 = plt.fill_between(pos_LIENSs_PPP.time, np.mean(pos_LIENSs_PPP.Surface_Height) - np.std(pos_LIENSs_PPP.Surface_Height),
#                           np.mean(pos_LIENSs_PPP.Surface_Height) + np.std(pos_LIENSs_PPP.Surface_Height), color='orange', alpha=0.2)
# fill_2 = plt.fill_between(pos_LIENSs_RTK.time, np.mean(pos_LIENSs_RTK.Surface_Height) - np.std(pos_LIENSs_RTK.Surface_Height),
#                           np.mean(pos_LIENSs_RTK.Surface_Height) + np.std(pos_LIENSs_RTK.Surface_Height), color='b', alpha=0.2)
# fill_3 = plt.fill_between(pos_Bouee2.time, np.mean(pos_Bouee2.Surface_Height) - np.std(pos_Bouee2.Surface_Height),
#                           np.mean(pos_Bouee2.Surface_Height) + np.std(pos_Bouee2.Surface_Height), color='r', alpha=0.2)
# fill_4 = plt.fill_between(maregraphe_barrage.time, np.mean(maregraphe_barrage.Height) - np.std(maregraphe_barrage.Height),
#                           np.mean(maregraphe_barrage.Height) + np.std(maregraphe_barrage.Height), color='g', alpha=0.2)

plt.xticks(rotation=20)
plt.xlabel('Date')
plt.ylabel('Hauteur ellipsoïdale [m]')
plt.legend()
plt.ylim([170.75, 171.25])
plt.title('Composante verticale')
plt.tight_layout()
plt.savefig(f"{FOLDER_SAVE}\\Comparaison_z_{SURCHARGE_OCEANO_LABEL}_fix.png")
# plt.show()


## Stat écart ## 
f_he = plt.figure(figsize=FIGURE_SIZE)
nb_vdc = len(dic_buoys.keys()) - 1
f_vdc, ax_vdc = plt.subplots(nrows=1, ncols=nb_vdc, figsize=FIGURE_SIZE)
i_vdc = 0

i_rap_max = len(dic_buoys.keys()) - 1
f_rapport, ax_rapport = plt.subplots(nrows=i_rap_max, ncols=1, figsize=FIGURE_SIZE)
# color_rapport =
i_rap = 0

for ib in range(len(dic_buoys.keys()) - 1):
    keys = list(dic_buoys.keys())
    buoy_name1 = keys[ib]
    buoy1 = dic_buoys[buoy_name1]
    
    for buoy_name2 in list(dic_buoys.keys())[ib+1:]:
        buoy2 = dic_buoys[buoy_name2]
        if buoy_name1 == 'LIENSs RTK':
            buoy2_interpolated_Surface_Height = np.interp(buoy1.time, buoy2.time, buoy2.Surface_Height) # Interpol sur les données RTK contenant un trou
            buoy1_interpolated_Surface_Height = buoy1.Surface_Height
            time = buoy1.time
        elif buoy_name2 == 'LIENSs RTK':
            buoy1_interpolated_Surface_Height = np.interp(buoy2.time, buoy1.time, buoy1.Surface_Height)
            buoy2_interpolated_Surface_Height = buoy2.Surface_Height
            time = buoy2.time
        else: # Not RTK on interpol sur la série temporelle LIENSs PPP
            buoy1_interpolated_Surface_Height = np.interp(pos_LIENSs_PPP.time, buoy1.time, buoy1.Surface_Height)
            buoy2_interpolated_Surface_Height = np.interp(pos_LIENSs_PPP.time, buoy2.time, buoy2.Surface_Height) # Interpol sur les données LIENSs PPP
            time = pos_LIENSs_PPP.time
            
        delta_buoy1_buoy2 = buoy2_interpolated_Surface_Height - buoy1_interpolated_Surface_Height
        plt.figure(f_he)
        plt.plot(time, delta_buoy1_buoy2, label=f'{buoy_name2} - {buoy_name1}')
        
        rmse_delta_buoy1_buoy2 = np.sqrt( np.sum(delta_buoy1_buoy2 ** 2) / len(delta_buoy1_buoy2) )
        iqr_delta_buoy1_buoy2 = iqr(delta_buoy1_buoy2[~np.isnan(delta_buoy1_buoy2)])
        std_delta_buoy1_buoy2 = np.std(delta_buoy1_buoy2)
        med_delta_buoy1_buoy2 = np.nanmedian(delta_buoy1_buoy2)
        mean_delta_buoy1_buoy2 = np.nanmean(delta_buoy1_buoy2)
        mad_delta_buoy1_buoy2 =  np.nanmedian(np.abs(delta_buoy1_buoy2 - med_delta_buoy1_buoy2)) * 1.4826
        std_iqr_delta_buoy1_buoy2 = iqr_delta_buoy1_buoy2 / 1.349
        lines_result.append('########################\n')
        lines_result.append(f'Hauteur ellipsoïdale (ramenée à la surface) - {buoy_name2} vs {buoy_name1}\n')
        lines_result.append(f'\tMean error: {mean_delta_buoy1_buoy2}m\n \
                            Median error: {med_delta_buoy1_buoy2}m\n \
                            Error std: {std_delta_buoy1_buoy2}m\n \
                            Error iqr: {iqr_delta_buoy1_buoy2}m\n \
                            RMSE: {rmse_delta_buoy1_buoy2}m\n \
                            MAD: {mad_delta_buoy1_buoy2}m\n \
                            STD_iqr: {std_iqr_delta_buoy1_buoy2}m\n')
        
        
        # Van de Casteele 
        if buoy_name2 == 'Marégraphe barrage':
            # plt.figure(f_vdc)
            ax = ax_vdc[i_vdc]
            ax.plot(delta_buoy1_buoy2, buoy2_interpolated_Surface_Height)
            ax.set_xlabel(r'$\Delta h$ [m]')
            ax.set_xlim([-0.2, 0.2])
            ax.set_ylim([171.05, 171])
            ax.axvline(x=0, linestyle='--', color='k')
            ax.set_title(buoy_name1)
            
            if i_vdc == 0:
                ax.set_ylabel('Hauteur ellipsoïdale [m]')
            # else:
            #     ax.set_yticks([])
                
            ax.grid(True)
            
            i_vdc += 1
            
            # plt.figure(f_rapport)
            ax = ax_rapport[i_rap]
            ax.plot(time, delta_buoy1_buoy2, label=buoy_name1, color=sns.color_palette()[i_rap])
            # ax.set_xlim([-0.2, 0.2])
            ax.set_ylim([-0.2, 0.4])
            # ax.axvline(x=0, linestyle='--', color='k')
            # ax.set_title(buoy_name1)
            
            if i_rap == i_rap_max-1:
                ax.set_xlabel('Date')
            elif i_rap == 1:
                ax.set_ylabel(r'Ecart au marégraphe radar [m]')

            ax.legend(loc='upper right')
            ax.grid(True)
            
            i_rap += 1

        
            


plt.figure(f_he)
plt.tight_layout()
plt.xticks(rotation=20)
plt.xlabel('Date')
plt.ylabel('Ecart [m]')
plt.legend()
plt.title('Evaluation des écarts')
plt.ylim([-0.2, 0.2])
plt.tight_layout()
plt.savefig(f"{FOLDER_SAVE}\\Comparaison_Error_z_{SURCHARGE_OCEANO_LABEL}_fix.png")
# plt.show()

# Diagramm de xvan de castel 
plt.figure(f_vdc)
plt.suptitle('Diagramme de Van de Casteele - Ref: Marégraphe')
# plt.tight_layout()
plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.4,
                    hspace=0.5)

plt.savefig(f"{FOLDER_SAVE}\\Van_DeCasteele_{SURCHARGE_OCEANO_LABEL}_fix.png")


# Comparaison des hateurs pour le rapport 
plt.figure(f_rapport)
plt.suptitle('Comparaison des écarts au marégraphe radar')
# plt.tight_layout()
plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.4,
                    hspace=0.5)
plt.savefig(f"{FOLDER_SAVE}\\Comp_maraegraphe_radar_{SURCHARGE_OCEANO_LABEL}_fix.png")

# pos_LIENSs_RTK.time += timedelta(seconds=5)


### Comparaison planimétrique ### 
plt.figure()
plt.plot(pos_Bouee2.time, pos_Bouee2.Longitude - 360, label='Bouée PPP')
plt.plot(pos_LIENSs_PPP.time, pos_LIENSs_PPP.Longitude - 360, label='LIENSS PPP')
plt.plot(pos_LIENSs_RTK.time, pos_LIENSs_RTK.Longitude, label='LIENSS RTK')
plt.xlabel('Date')
plt.ylabel('Longitude [°]')
plt.legend()
plt.title('Longitude')
plt.tight_layout()
plt.savefig(f"{FOLDER_SAVE}\\Lon_{SURCHARGE_OCEANO_LABEL}_fix.png")

plt.figure()
plt.plot(pos_Bouee2.time, pos_Bouee2.Latitude, label='Bouée PPP')
plt.plot(pos_LIENSs_PPP.time, pos_LIENSs_PPP.Latitude, label='LIENSS PPP')
plt.plot(pos_LIENSs_RTK.time, pos_LIENSs_RTK.Latitude, label='LIENSS RTK')
plt.xlabel('Date')
plt.ylabel('Latitude [°]')
plt.legend()
plt.title('Latitude')
plt.tight_layout()
plt.savefig(f"{FOLDER_SAVE}\\Lat_{SURCHARGE_OCEANO_LABEL}_fix.png")



plt.figure()
plt.scatter(pos_Bouee2.Longitude - 360, pos_Bouee2.Latitude, label='Bouée PPP', s=5)
plt.scatter(pos_LIENSs_PPP.Longitude - 360, pos_LIENSs_PPP.Latitude, label='LIENSS PPP', s=5)
plt.scatter(pos_LIENSs_RTK.Longitude, pos_LIENSs_RTK.Latitude, label='LIENSS RTK', s=5)
plt.xlabel('Longitude [°]')
plt.ylabel('Latitude [°]')
plt.legend()
plt.title('Trajectographie en coordonnées géographiques - ITRF14')
plt.tight_layout()
plt.savefig(f"{FOLDER_SAVE}\\Trajecto_{SURCHARGE_OCEANO_LABEL}_fix.png")


plt.figure()
plt.scatter(pos_Bouee2.X, pos_Bouee2.Y, label='Bouée PPP', s=5)
plt.scatter(pos_LIENSs_PPP.X, pos_LIENSs_PPP.Y, label='LIENSS PPP', s=5)
plt.scatter(pos_LIENSs_RTK.X, pos_LIENSs_RTK.Y, label='LIENSS RTK', s=5)
plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.legend()
plt.title('Trajectographie en coordonnées géocentrique - ITRF14')
plt.tight_layout()
plt.savefig(f"{FOLDER_SAVE}\\Trajecto_geoc_{SURCHARGE_OCEANO_LABEL}_fix.png")

plt.show()


# Ecart total
delta_tot_xyz_LIENSS_PPP_Bouee2 = np.sqrt( (pos_Bouee2.X - pos_LIENSs_PPP.X)**2 + (pos_Bouee2.Y - pos_LIENSs_PPP.Y)**2 +(pos_Bouee2.Z - pos_LIENSs_PPP.Z)**2) 
rmse_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.sqrt( np.sum(delta_tot_xyz_LIENSS_PPP_Bouee2 ** 2) / len(delta_tot_xyz_LIENSS_PPP_Bouee2) )
iqr_delta_tot_xyz_LIENSS_PPP_Bouee2 = iqr(delta_tot_xyz_LIENSS_PPP_Bouee2[~np.isnan(delta_tot_xyz_LIENSS_PPP_Bouee2)])
std_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.std(delta_tot_xyz_LIENSS_PPP_Bouee2)
med_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.nanmedian(delta_tot_xyz_LIENSS_PPP_Bouee2)
mean_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.nanmean(delta_tot_xyz_LIENSS_PPP_Bouee2)

lines_result.append('########################\n')
lines_result.append('Composante xyz - LIENSs PPP vs Bouée PPP\n')
lines_result.append(f'Mean error: {mean_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_PPP_Bouee2}m\n')

# print('Composante xyz: LIENSS PPP vs Bouee PPP')
# print(f'Mean error: {mean_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_PPP_Bouee2}m\n')


delta_tot_xyz_LIENSS_RTK_Bouee2 = np.sqrt( (pos_Bouee2.X - pos_LIENSs_RTK.X)**2 + (pos_Bouee2.Y - pos_LIENSs_RTK.Y)**2 +(pos_Bouee2.Z - pos_LIENSs_RTK.Z)**2) 
rmse_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.sqrt( np.sum(delta_tot_xyz_LIENSS_RTK_Bouee2 ** 2) / len(delta_tot_xyz_LIENSS_RTK_Bouee2) )
iqr_delta_tot_xyz_LIENSS_RTK_Bouee2 = iqr(delta_tot_xyz_LIENSS_RTK_Bouee2[~np.isnan(delta_tot_xyz_LIENSS_RTK_Bouee2)])
std_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.std(delta_tot_xyz_LIENSS_RTK_Bouee2)
med_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.nanmedian(delta_tot_xyz_LIENSS_RTK_Bouee2)
mean_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.nanmean(delta_tot_xyz_LIENSS_RTK_Bouee2)

lines_result.append('########################\n')
lines_result.append('Composante xyz - Bouée ENSTA PPP vs LIENSs RTK\n')
lines_result.append(f'Mean error: {mean_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_RTK_Bouee2}m\n')

# print('Composante xyz: LIENSS RTK vs Bouee PPP')
# print(f'Mean error: {mean_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_RTK_Bouee2}m\n')

delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.sqrt( (pos_LIENSs_PPP.X - pos_LIENSs_RTK.X)**2 + (pos_LIENSs_PPP.Y - pos_LIENSs_RTK.Y)**2 +(pos_LIENSs_PPP.Z - pos_LIENSs_RTK.Z)**2) 
rmse_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.sqrt( np.sum(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP ** 2) / len(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP) )
iqr_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = iqr(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP[~np.isnan(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)])
std_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.std(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)
med_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.nanmedian(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)
mean_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.nanmean(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)

lines_result.append('########################\n')
lines_result.append('Composante xyz - LIENSs PPP vs LIENSs RTK\n')
lines_result.append(f'Mean error: {mean_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nMedian error: {med_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nError std: {std_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\n')

# print('Composante xyz: LIENSS RTK vs LIENSS PPP')
# print(f'Mean error: {mean_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nMedian error: {med_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nError std: {std_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\n')


# Ecart x, y 
delta_tot_xyz_LIENSS_PPP_Bouee2 = np.sqrt( (pos_Bouee2.X - pos_LIENSs_PPP.X)**2 + (pos_Bouee2.Y - pos_LIENSs_PPP.Y)**2) 
rmse_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.sqrt( np.sum(delta_tot_xyz_LIENSS_PPP_Bouee2 ** 2) / len(delta_tot_xyz_LIENSS_PPP_Bouee2) )
iqr_delta_tot_xyz_LIENSS_PPP_Bouee2 = iqr(delta_tot_xyz_LIENSS_PPP_Bouee2[~np.isnan(delta_tot_xyz_LIENSS_PPP_Bouee2)])
std_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.std(delta_tot_xyz_LIENSS_PPP_Bouee2)
med_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.nanmedian(delta_tot_xyz_LIENSS_PPP_Bouee2)
mean_delta_tot_xyz_LIENSS_PPP_Bouee2 = np.nanmean(delta_tot_xyz_LIENSS_PPP_Bouee2)

# lines_result.append('########################\n')
# lines_result.append('Composante xyz - LIENSs PPP vs Bouée ENSTA PPP\n')
# lines_result.append(f'Mean error: {mean_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_PPP_Bouee2}m\n')

# print('Composante xy: LIENSS PPP vs Bouee PPP')
# print(f'Mean error: {mean_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_PPP_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_PPP_Bouee2}m\n')


delta_tot_xyz_LIENSS_RTK_Bouee2 = np.sqrt( (pos_Bouee2.X - pos_LIENSs_RTK.X)**2 + (pos_Bouee2.Y - pos_LIENSs_RTK.Y)**2 ) 
rmse_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.sqrt( np.sum(delta_tot_xyz_LIENSS_RTK_Bouee2 ** 2) / len(delta_tot_xyz_LIENSS_RTK_Bouee2) )
iqr_delta_tot_xyz_LIENSS_RTK_Bouee2 = iqr(delta_tot_xyz_LIENSS_RTK_Bouee2[~np.isnan(delta_tot_xyz_LIENSS_RTK_Bouee2)])
std_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.std(delta_tot_xyz_LIENSS_RTK_Bouee2)
med_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.nanmedian(delta_tot_xyz_LIENSS_RTK_Bouee2)
mean_delta_tot_xyz_LIENSS_RTK_Bouee2 = np.nanmean(delta_tot_xyz_LIENSS_RTK_Bouee2)


print('Composante xy: LIENSS RTK vs Bouee PPP')
print(f'Mean error: {mean_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nMedian error: {med_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nError std: {std_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_RTK_Bouee2}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_RTK_Bouee2}m\n')

delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.sqrt( (pos_LIENSs_PPP.X - pos_LIENSs_RTK.X)**2 + (pos_LIENSs_PPP.Y - pos_LIENSs_RTK.Y)**2) 
rmse_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.sqrt( np.sum(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP ** 2) / len(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP) )
iqr_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = iqr(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP[~np.isnan(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)])
std_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.std(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)
med_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.nanmedian(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)
mean_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP = np.nanmean(delta_tot_xyz_LIENSS_RTK_LIENSS_PPP)
print('Composante xy: LIENSS RTK vs LIENSS PPP')
print(f'Mean error: {mean_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nMedian error: {med_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nError std: {std_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nError iqr: {iqr_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\nRMSE: {rmse_delta_tot_xyz_LIENSS_RTK_LIENSS_PPP}m\n')


with open(FILE_RESULT, 'w') as f:
    f.writelines(lines_result)
    

### OLD VERSION ### 
# # Stat des écarts
# plt.figure()
# ### LIENSS vs Bouee ###
# #Interp at same date 
# pos_Bouee2_Interpolated_Surface_Height = np.interp(pos_LIENSs_PPP.time, pos_Bouee2.time, pos_Bouee2.Surface_Height)
# delta_LIENSS_Bouee2 = pos_LIENSs_PPP.Surface_Height - pos_Bouee2_Interpolated_Surface_Height
# plt.plot(pos_LIENSs_PPP.time, delta_LIENSS_Bouee2, label='LIENSS PPP - Bouée PPP')

# rmse_delta_LIENSS_Bouee2 = np.sqrt( np.sum(delta_LIENSS_Bouee2 ** 2) / len(delta_LIENSS_Bouee2) )
# iqr_delta_LIENSS_Bouee2 = iqr(delta_LIENSS_Bouee2)
# std_delta_LIENSS_Bouee2 = np.std(delta_LIENSS_Bouee2)
# med_delta_LIENSS_Bouee2 = np.median(delta_LIENSS_Bouee2)
# mean_delta_LIENSS_Bouee2 = np.mean(delta_LIENSS_Bouee2)
# lines_result.append('########################\n')
# lines_result.append('Hauteur ellipsoïdale - LIENSs PPP vs Bouée ENSTA PPP\n')
# lines_result.append(f'Mean error: {mean_delta_LIENSS_Bouee2}m\nMedian error: {med_delta_LIENSS_Bouee2}m\nError std: {std_delta_LIENSS_Bouee2}m\nError iqr: {iqr_delta_LIENSS_Bouee2}m\nRMSE: {rmse_delta_LIENSS_Bouee2}m\n')
# # print('Hauteur LIENSS PPP vs Bouée')
# # print(f'Mean error: {mean_delta_LIENSS_Bouee2}m\nMedian error: {med_delta_LIENSS_Bouee2}m\nError std: {std_delta_LIENSS_Bouee2}m\nError iqr: {iqr_delta_LIENSS_Bouee2}m\nRMSE: {rmse_delta_LIENSS_Bouee2}m\n')

# ### Maregraphe vs Bouee ##
# # maregraphe_Interpolated_Surface_Height_Bouee = np.interp(pos_Bouee2.time, maregraphe_barrage.time, maregraphe_barrage.Height)
# maregraphe_Interpolated_Surface_Height_Bouee = np.interp(pos_LIENSs_PPP.time, maregraphe_barrage.time, maregraphe_barrage.Height)

# # delta_Maregraphe_Bouee2 = maregraphe_Interpolated_Surface_Height_Bouee - pos_Bouee2.Surface_Height
# delta_Maregraphe_Bouee2 = maregraphe_Interpolated_Surface_Height_Bouee - pos_Bouee2_Interpolated_Surface_Height

# plt.plot(pos_LIENSs_PPP.time, delta_Maregraphe_Bouee2, label='Marégraphe barrage - Bouée PPP')

# rmse_delta_Maregraphe_Bouee2 = np.sqrt( np.sum(delta_Maregraphe_Bouee2 ** 2) / len(delta_Maregraphe_Bouee2) )
# iqr_delta_Maregraphe_Bouee2 = iqr(delta_Maregraphe_Bouee2)
# std_delta_Maregraphe_Bouee2 = np.std(delta_Maregraphe_Bouee2)
# med_delta_Maregraphe_Bouee2 = np.median(delta_Maregraphe_Bouee2)
# mean_delta_Maregraphe_Bouee2 = np.mean(delta_Maregraphe_Bouee2)

# lines_result.append('########################\n')
# lines_result.append('Hauteur ellipsoïdale - Marégaphe vs Bouée ENSTA PPP\n')
# lines_result.append(f'Mean error: {mean_delta_Maregraphe_Bouee2}m\nMedian error: {med_delta_Maregraphe_Bouee2}m\nError std: {std_delta_Maregraphe_Bouee2}m\nError iqr: {iqr_delta_Maregraphe_Bouee2}m\nRMSE: {rmse_delta_Maregraphe_Bouee2}m\n')

# # print('Hauteur Maregaphe vs Bouée')
# # print(f'Mean error: {mean_delta_Maregraphe_Bouee2}m\nMedian error: {med_delta_Maregraphe_Bouee2}m\nError std: {std_delta_Maregraphe_Bouee2}m\nError iqr: {iqr_delta_Maregraphe_Bouee2}m\nRMSE: {rmse_delta_Maregraphe_Bouee2}m\n')


# ### Maregraphe vs LIENSS PPP##
# maregraphe_Interpolated_Surface_Height_LIENSS_PPP = np.interp(pos_LIENSs_PPP.time, maregraphe_barrage.time, maregraphe_barrage.Height)
# delta_Maregraphe_LIENSS_PPP = maregraphe_Interpolated_Surface_Height_LIENSS_PPP - pos_LIENSs_PPP.Surface_Height
# plt.plot(pos_LIENSs_PPP.time, delta_Maregraphe_LIENSS_PPP, label='Marégraphe - LIENSS PPP')

# rmse_delta_Maregraphe_LIENSS_PPP = np.sqrt( np.sum(delta_Maregraphe_LIENSS_PPP ** 2) / len(delta_Maregraphe_LIENSS_PPP) )
# iqr_delta_Maregraphe_LIENSS_PPP = iqr(delta_Maregraphe_LIENSS_PPP)
# std_delta_Maregraphe_LIENSS_PPP = np.std(delta_Maregraphe_LIENSS_PPP)
# med_delta_Maregraphe_LIENSS_PPP = np.median(delta_Maregraphe_LIENSS_PPP)
# mean_delta_Maregraphe_LIENSS_PPP = np.mean(delta_Maregraphe_LIENSS_PPP)

# lines_result.append('########################\n')
# lines_result.append('Hauteur ellipsoïdale - Marégaphe vs LIENSs PPP\n')
# lines_result.append(f'Mean error: {mean_delta_Maregraphe_LIENSS_PPP}m\nMedian error: {med_delta_Maregraphe_LIENSS_PPP}m\nError std: {std_delta_Maregraphe_LIENSS_PPP}m\nError iqr: {iqr_delta_Maregraphe_LIENSS_PPP}m\nRMSE: {rmse_delta_Maregraphe_LIENSS_PPP}m\n')

# # print('HauteurMaregaphe vs LIENSS PPP')
# # print(f'Mean error: {mean_delta_Maregraphe_LIENSS_PPP}m\nMedian error: {med_delta_Maregraphe_LIENSS_PPP}m\nError std: {std_delta_Maregraphe_LIENSS_PPP}m\nError iqr: {iqr_delta_Maregraphe_LIENSS_PPP}m\nRMSE: {rmse_delta_Maregraphe_LIENSS_PPP}m\n')

# ### Maregraphe vs LIENSS RTK##
# maregraphe_Interpolated_Surface_Height_LIENSS_RTK = np.interp(pos_LIENSs_RTK.time, maregraphe_barrage.time, maregraphe_barrage.Height)
# delta_Maregraphe_LIENSS_RTK = maregraphe_Interpolated_Surface_Height_LIENSS_RTK - pos_LIENSs_RTK.Surface_Height
# plt.plot(pos_LIENSs_RTK.time, delta_Maregraphe_LIENSS_RTK, label='Marégraphe - LIENSS RTK')

# rmse_delta_Maregraphe_LIENSS_RTK = np.sqrt( np.sum(delta_Maregraphe_LIENSS_RTK ** 2) / len(delta_Maregraphe_LIENSS_RTK) )
# iqr_delta_Maregraphe_LIENSS_RTK = iqr(delta_Maregraphe_LIENSS_RTK[~np.isnan(delta_Maregraphe_LIENSS_RTK)])
# std_delta_Maregraphe_LIENSS_RTK = np.std(delta_Maregraphe_LIENSS_RTK)
# med_delta_Maregraphe_LIENSS_RTK = np.nanmedian(delta_Maregraphe_LIENSS_RTK)
# mean_delta_Maregraphe_LIENSS_RTK = np.nanmean(delta_Maregraphe_LIENSS_RTK)

# lines_result.append('########################\n')
# lines_result.append('Hauteur ellipsoïdale - Marégaphe vs LIENSs RTK\n')
# lines_result.append(f'Mean error: {mean_delta_Maregraphe_LIENSS_RTK}m\nMedian error: {med_delta_Maregraphe_LIENSS_RTK}m\nError std: {std_delta_Maregraphe_LIENSS_RTK}m\nError iqr: {iqr_delta_Maregraphe_LIENSS_RTK}m\nRMSE: {rmse_delta_Maregraphe_LIENSS_RTK}m\n')

# # print('Hauteur Maregaphe vs LIENSS RTK')
# # print(f'Mean error: {mean_delta_Maregraphe_LIENSS_RTK}m\nMedian error: {med_delta_Maregraphe_LIENSS_RTK}m\nError std: {std_delta_Maregraphe_LIENSS_RTK}m\nError iqr: {iqr_delta_Maregraphe_LIENSS_RTK}m\nRMSE: {rmse_delta_Maregraphe_LIENSS_RTK}m\n')

# delta_z_LIENSS_RTK_LIENSS_PPP = pos_LIENSs_PPP.Height - pos_LIENSs_RTK.Height
# rmse_delta_z_LIENSS_RTK_LIENSS_PPP = np.sqrt( np.sum(delta_z_LIENSS_RTK_LIENSS_PPP ** 2) / len(delta_z_LIENSS_RTK_LIENSS_PPP) )
# iqr_delta_z_LIENSS_RTK_LIENSS_PPP = iqr(delta_z_LIENSS_RTK_LIENSS_PPP[~np.isnan(delta_z_LIENSS_RTK_LIENSS_PPP)])
# std_delta_z_LIENSS_RTK_LIENSS_PPP = np.std(delta_z_LIENSS_RTK_LIENSS_PPP)
# med_delta_z_LIENSS_RTK_LIENSS_PPP = np.nanmedian(delta_z_LIENSS_RTK_LIENSS_PPP)
# mean_delta_z_LIENSS_RTK_LIENSS_PPP = np.nanmean(delta_z_LIENSS_RTK_LIENSS_PPP)

# lines_result.append('########################\n')
# lines_result.append('Hauteur ellipsoïdale - LIENSs PPP vs LIENSs RTK\n')
# lines_result.append(f'Mean error: {mean_delta_z_LIENSS_RTK_LIENSS_PPP}m\nMedian error: {med_delta_z_LIENSS_RTK_LIENSS_PPP}m\nError std: {std_delta_z_LIENSS_RTK_LIENSS_PPP}m\nError iqr: {iqr_delta_z_LIENSS_RTK_LIENSS_PPP}m\nRMSE: {rmse_delta_z_LIENSS_RTK_LIENSS_PPP}m\n')

# # print('Hauteur LIENSS RTK vs LIENSS PPP')
# # print(f'Mean error: {mean_delta_z_LIENSS_RTK_LIENSS_PPP}m\nMedian error: {med_delta_z_LIENSS_RTK_LIENSS_PPP}m\nError std: {std_delta_z_LIENSS_RTK_LIENSS_PPP}m\nError iqr: {iqr_delta_z_LIENSS_RTK_LIENSS_PPP}m\nRMSE: {rmse_delta_z_LIENSS_RTK_LIENSS_PPP}m\n')

# plt.figure()
# plt.subplot(131)
# plt.plot(delta_Maregraphe_Bouee2, maregraphe_Interpolated_Surface_Height_Bouee)
# plt.xlabel(r'$\Delta h$')
# plt.xlim([-0.2, 0.2])
# plt.axvline(x=0, linestyle='--', color='k')
# # plt.legend()
# plt.title('Bouée PPP')

# plt.subplot(132)
# plt.plot(delta_Maregraphe_LIENSS_PPP, maregraphe_Interpolated_Surface_Height_LIENSS_PPP)
# plt.xlabel(r'$\Delta h$')
# plt.xlim([-0.2, 0.2])
# plt.axvline(x=0, linestyle='--', color='k')
# # plt.legend()
# plt.title('LIENSS PPP')

# plt.subplot(133)
# plt.plot(delta_Maregraphe_LIENSS_RTK, maregraphe_Interpolated_Surface_Height_LIENSS_RTK)
# plt.xlabel(r'$\Delta h$')
# plt.xlim([-0.2, 0.2])
# plt.axvline(x=0, linestyle='--', color='k')
# # plt.legend()
# plt.title('LIENSS RTK')

# plt.suptitle('Diagramme de Van de Casteele - Ref: Marégraphe')
# plt.ylabel('Hauteur ellipsoïdale [m]')
# plt.tight_layout()
# plt.savefig(f"{FOLDER_SAVE}\\Van_DeCasteele_LIENSSPPP_LIENSSRTK_BoueePPP_Maregraphe_fix.png")
# plt.show()
# plt.show()
# plt.figure()
# plt.xlabel(r'$\Delta h$')
# plt.xlim([-0.2, 0.2])
# plt.axvline(x=0, linestyle='--', color='k')