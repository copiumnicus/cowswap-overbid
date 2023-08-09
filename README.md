# cowswap overbid

small analysis i did on overbidding, I got rid of the data collection left a stub (I was getting auction ids from telegram msgs), got rid of some my solver specific analysis


## Install
```bash
pip3 install -r requirements.txt
```

## Decompress data
```bash
tar -xzf last_week_partial.tar.gz
```

## Run
```bash
sh ./process.sh
```

![Overbidders](./overbidder.png)