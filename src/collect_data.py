import requests

# make it smaller 
def remap_auction(a):
    obj = {}
    for k in ["auctionId", "transactionHash", "gasPrice", "competitionSimulationBlock", "solutions"]:
        if k in a:
            obj[k] = a[k]
        else:
            print("got", a)
    return obj

# /api/v1/solver_competition/{auction_id}
def get_auction(auction_id):
    compEndpointUrl = "https://api.cow.fi/mainnet/api/v1/solver_competition/" + \
        str(auction_id)
    response = requests.get(compEndpointUrl)
    if response.status_code == 403:
        import time
        time.sleep(1.0)
        return get_auction(auction_id)
    res = response.json()
    if "errorType" in res:
        print("failed to get auction", auction_id)
    return res

# MAKE AUCTIONS SMALLER AND USABLE IN DATAFRAME
def reindex(auction):
    new_data = []
    if "auctionId" in auction:
        for sol in auction["solutions"]:
            copied = auction.copy()
            del copied["solutions"]
            copied.update(sol)
            new_data.append(copied)
    return new_data

def get_auctions(name, refs):
    end = len(refs)
    index = 0
    auctions = []
    for r in refs:
        prcent = (index / end) * 100.0
        print(prcent, "%")
        try:
            obj = remap_auction(get_auction(r))
            if "auctionId" in obj:
                auctions.extend(reindex(obj))
        except Exception as e:
            print("something failed", e)
        index += 1


    import json
    file = open(name+ "-auctions.json", 'w')
    file.write(json.dumps(auctions))

# I got the auction ids from my telegram msgs, i'll spare you the code
# The above is more or less what I used should work with other data source
name = "last-week"
auction_ids = []
# get_auctions(name, auction_ids)
