Ubx2ConcatRnx convertit les données UBX en RNX concaténés et journaliers.
L'arborescense des fichiers est la suivante :
  L'ensemble des données est contenu dans le dossier nommé root_dir dans le code
  Ce dossier doit contenir un sous-dossier UBX dans lequel sont stockées les UBX
  Une fois le traitement fini, plusieurs dossiers RNX sont créés (RNX_3.05_TADJ par exemple)
  Ces dossiers contiennent :
    les RNX horaires correspondant aux UBX
    Un dossier concat dans lequel sont stockés les fichiers RNX concaténés (un fichier avec l'ensemble des informations et des fichiers journaliers)
Ubx2ConcatRnx prend en entrée :
  le fichier root_dir
  la version de RINEX que l'on souhaite (3.05 par défaut)
  Un booléen nommé TADJ. Si TADJ == True, les secondes des observarions des RINEX sont entières.
  Le paramètre verbose n'a pas d'influence sur les traitements, il change juste le niveau d'informations retournées dans la console par l'algorithme
 Ubx2ConcatRnx appelle plusieurs autres scripts :
  ExtractGz : extrait les UBX si ces derniers sont données sous un format compressé .gz
  Ubx2Rnx : convertit les UBX extraits en RNX (Chaque RNX créé correspond à un UBX)
  ConcatRnx : concatène les fichiers RNX. On obtient un fichier RNX avec toutes les observations, ainsi que des fichiers journaliers.s

