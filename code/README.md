```bash 
sed -n '13619,15335p;15335q' log_opendap_MERRA2.txt  | parallel -j 1 python opendap_MERRA2_download_per_station_bash.py :::: &> log_opendap_MERRA2_new.txt
```


